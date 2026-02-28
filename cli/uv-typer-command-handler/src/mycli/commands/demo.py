import typer

from mycli.tui import TUI

app = typer.Typer(help="Demo interactive prompts")


@app.command("prompts")
def prompts(ctx: typer.Context) -> None:
    """Try out checkbox, select, confirm, and text prompts."""
    tui: TUI = ctx.obj["tui"]

    selected = tui.checkbox("Pick toppings:", ["cheese", "pepperoni", "mushrooms", "olives"])
    tui.success(f"Toppings: {', '.join(selected) or 'none'}")

    size = tui.select("Pick a size:", ["small", "medium", "large"])
    tui.success(f"Size: {size}")

    name = tui.prompt("Your name?")
    tui.success(f"Name: {name}")

    if tui.confirm("Place order?"):
        tui.success("Order placed!")
    else:
        tui.info("Cancelled")
