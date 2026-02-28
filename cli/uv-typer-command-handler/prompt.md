 
```bash
# path: /Users/alek/code/work/agentic-infra/templates/cli/uv-typer-command-handler
> pbpaste
To use green checkmarks for boxes in a Python command-line interface, questionary relies on Unicode characters and terminal support. While questionary automatically handles some selection styling, you can explicitly use the Heavy Checkmark Unicode character (✅ - ✅) or the standard checkmark (✔ - ✔) within the choices of a questionary.checkbox prompt to make them appear green in terminals that support color. 
Super User
Super User
 +2
Implementation in Python
python
import questionary

# Define choices with unicode checkmarks
choices = [
    "✅ Feature One",
    "✅ Feature Two",
    "❌ Feature Three" # You can use other symbols too
]

# Use questionary.checkbox
selected_features = questionary.checkbox(
    "Select the features to enable:",
    choices=choices
).ask()

print("Selected:", selected_features)
Key Considerations
Unicode Support: Ensure your terminal (e.g., Windows Terminal, iTerm2, VS Code Terminal) supports UTF-8 and displays Unicode emojis/symbols.
Terminal Color: The green color often depends on the terminal's default emoji rendering or the theme of the command-line tool.
Alternative (Custom Styling): questionary allows for custom styling if you want to change the color of the selection arrow or brackets, rather than just using a coloured emoji symbol.
Checkmark Code: You can use ✅ for a green, boxed checkmark (✅) or ✔️ for a stylized checkmark (✔️). 
```

