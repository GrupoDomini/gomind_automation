from setuptools import setup

setup(
    name="gomind_automation",
    python_requires=">=3.6",
    version="1.0.0",
    description="GoMind automation functions - Add block functions",
    url="https://github.com/GrupoDomini/gomind_automation.git",
    author="JeffersonCarvalhoGD",
    author_email="jefferson.carvalho@grupodomini.com",
    license="unlicense",
    packages=["gomind_automation"],
    zip_safe=False,
    install_requires=[
        "pyautogui",
        "pyperclip",
        "opencv-python",
        "pynput",
        "keyboard"
    ],
)
