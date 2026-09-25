from pathlib import Path

from fastapi import (
    APIRouter,
    Request,
    Form,
    HTTPException
)

from fastapi.responses import (
    HTMLResponse
)

from fastapi.templating import Jinja2Templates

from .schemas import (
    UserInput,
    FeedbackRequest
)

from .database import (
    save_user,
    save_plan,
    get_user,
    get_latest_plan,
    update_plan,
    get_all_users
)

from .ai.gemini_generator import (
    generate_workout_gemini
)

from .ai.gemini_flash_generator import (
    generate_nutrition_tip_with_flash
)

from .ai.updated_plan import (
    update_workout_plan
)

from .config import ADMIN_KEY


router = APIRouter()


BASE_DIR = Path(
    __file__
).resolve().parent.parent


templates = Jinja2Templates(
    directory=str(
        BASE_DIR / "templates"
    )
)


def render_error(
    request,
    message,
    status=400
):

    return templates.TemplateResponse(

        request=request,

        name="error.html",

        context={
            "message": message
        },

        status_code=status
    )


@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={}
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(

    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...)
):

    try:

        data = UserInput(

            username=username,

            user_id=user_id,

            age=age,

            weight=weight,

            goal=goal,

            intensity=intensity
        )

        user_pk = save_user(data)


        class UserForAI:
            pass


        user = UserForAI()

        user.username = data.username
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity


        workout = generate_workout_gemini(
            user
        )


        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                user
            )
        )


        plan_id = save_plan(

            user_pk,

            workout,

            nutrition_tip
        )


        return templates.TemplateResponse(

            request=request,

            name="result.html",

            context={

                "username": data.username,

                "user_id": data.user_id,

                "age": data.age,

                "weight": data.weight,

                "goal": data.goal,

                "intensity": data.intensity,

                "workout_plan": workout,

                "nutrition_tip": nutrition_tip,

                "plan_id": plan_id,

                "updated": False,

                "feedback": None
            }
        )


    except ValueError as exc:

        return render_error(
            request,
            str(exc)
        )


    except Exception as exc:

        return render_error(

            request,

            f"Could not generate the plan: {exc}",

            500
        )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...)
):

    try:

        data = FeedbackRequest(

            user_id=user_id,

            feedback=feedback
        )


        user = get_user(
            data.user_id
        )


        plan = get_latest_plan(
            data.user_id
        )


        if not user or not plan:

            return render_error(

                request,

                "User or workout plan was not found.",

                404
            )


        updated_plan = update_workout_plan(

            plan.original_plan,

            data.feedback,

            user
        )


        update_plan(

            plan.id,

            updated_plan,

            data.feedback
        )


        return templates.TemplateResponse(

            request=request,

            name="result.html",

            context={

                "username": user.username,

                "user_id": user.user_id,

                "age": user.age,

                "weight": user.weight,

                "goal": user.goal,

                "intensity": user.intensity,

                "workout_plan": updated_plan,

                "nutrition_tip": plan.nutrition_tip,

                "plan_id": plan.id,

                "updated": True,

                "feedback": data.feedback
            }
        )


    except ValueError as exc:

        return render_error(
            request,
            str(exc)
        )


    except Exception as exc:

        return render_error(

            request,

            f"Could not update the plan: {exc}",

            500
        )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(

    request: Request,

    key: str = ""
):

    if key != ADMIN_KEY:

        return render_error(

            request,

            "Invalid admin key.",

            403
        )


    users = get_all_users()


    return templates.TemplateResponse(

        request=request,

        name="all_users.html",

        context={

            "users": users,

            "admin_key": key
        }
    )


@router.get(
    "/api/health"
)
def health():

    return {

        "status": "ok",

        "service": "FitBuddy"
    }


@router.post(
    "/api/generate-workout"
)
def api_generate(
    data: UserInput
):

    try:

        class UserForAI:
            pass


        user = UserForAI()

        user.username = data.username
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity


        user_pk = save_user(data)


        workout = generate_workout_gemini(
            user
        )


        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                user
            )
        )


        plan_id = save_plan(

            user_pk,

            workout,

            nutrition_tip
        )


        return {

            "plan_id": plan_id,

            "workout_plan": workout,

            "nutrition_tip": nutrition_tip
        }


    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=str(exc)
        )


@router.post(
    "/api/submit-feedback"
)
def api_feedback(
    data: FeedbackRequest
):

    user = get_user(
        data.user_id
    )

    plan = get_latest_plan(
        data.user_id
    )


    if not user or not plan:

        raise HTTPException(

            status_code=404,

            detail="User or plan not found"
        )


    try:

        updated = update_workout_plan(

            plan.original_plan,

            data.feedback,

            user
        )


        update_plan(

            plan.id,

            updated,

            data.feedback
        )


        return {

            "plan_id": plan.id,

            "updated_plan": updated
        }


    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=str(exc)
        )


@router.get(
    "/api/users"
)
def api_users():

    users = get_all_users()


    return [

        {

            "user_id": user.user_id,

            "username": user.username,

            "age": user.age,

            "weight": user.weight,

            "goal": user.goal,

            "intensity": user.intensity,

            "plans": [

                {

                    "id": plan.id,

                    "original_plan":
                        plan.original_plan,

                    "updated_plan":
                        plan.updated_plan,

                    "feedback":
                        plan.feedback,

                    "nutrition_tip":
                        plan.nutrition_tip

                }

                for plan in user.plans

            ]
        }

        for user in users
    ]