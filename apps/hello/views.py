from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.hello.models import Message


def hello_world(request: HttpRequest) -> HttpResponse:
    greeting = Message.objects.filter(parent=None).order_by("-created_at").first()
    if greeting:
        responses = greeting.responses.all()
    else:
        responses = Message.objects.none()
    return render(
        request,
        "hello/hello_world.html",
        {
            "greeting": greeting,
            "responses": responses,
        },
    )


def create_greeting(request: HttpRequest) -> HttpResponse:
    """Create a new greeting."""
    error = None
    if request.method == "POST":
        content = request.POST.get("message", "").strip()
        author_name = (
            request.POST.get("author_name", "Anonymous").strip() or "Anonymous"
        )
        if content:
            greeting = Message.objects.create(
                content=content, author_name=author_name, parent=None
            )
            return redirect("greeting_detail", greeting_id=greeting.id)
        else:
            error = "Message cannot be empty."
    return render(request, "hello/create_greeting.html", {"error": error})


def greeting_detail(request: HttpRequest, greeting_id: int) -> HttpResponse:
    """Display a specific greeting with its responses and allow adding new responses."""
    try:
        greeting = Message.objects.get(id=greeting_id, parent=None)
    except Message.DoesNotExist:
        return render(request, "hello/greeting_not_found.html")
    responses = greeting.responses.all()
    return render(
        request,
        "hello/greeting_detail.html",
        {
            "greeting": greeting,
            "responses": responses,
        },
    )


def add_response(request: HttpRequest, greeting_id: int) -> HttpResponse:
    """Add a response to a greeting."""
    error = None
    if request.method == "POST":
        try:
            greeting = Message.objects.get(id=greeting_id, parent=None)
        except Message.DoesNotExist:
            return render(request, "hello/greeting_not_found.html")
        author_name = request.POST.get("author_name", "").strip() or "Anonymous"
        reply = request.POST.get("reply", "").strip()
        if author_name and reply:
            Message.objects.create(
                content=reply, author_name=author_name, parent=greeting
            )
            return redirect("greeting_detail", greeting_id=greeting_id)
        else:
            error = "Both name and reply are required."
            responses = greeting.responses.all()
            return render(
                request,
                "hello/greeting_detail.html",
                {
                    "greeting": greeting,
                    "responses": responses,
                    "error": error,
                },
            )
    return redirect("greeting_detail", greeting_id=greeting_id)


def list_greetings(request: HttpRequest) -> HttpResponse:
    """List all greetings."""
    greetings = Message.objects.filter(parent=None).order_by("-created_at")
    return render(
        request,
        "hello/list_greetings.html",
        {"greetings": greetings},
    )
