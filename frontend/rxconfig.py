import reflex as rx
from frontend.style import create_colors_dict

config = rx.Config(
    app_name="frontend",
    tailwind={
        "darkMode": "class",
        "theme": {
            "colors": {
                **create_colors_dict(),
            },
        },
    },
)
