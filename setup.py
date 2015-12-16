from setuptools import setup

setup(
    name="pyqtcli",
    version="0.5.0",
    description="CLI tool to help managing PyQt5 project",
    author="Kynarth Alseif",
    author_email="kynarth.alseif@gmail.com",
    packages=["pyqtcli"],
    include_package_data=True,
    install_requires=["click>=6.2", "colorama>=0.3.3", "lxml>=3.4.4"],
    entry_points="""
        [console_scripts]
        pyqtcli=pyqtcli.cli:pyqtcli
    """,
    license="MIT",
    zip_safe=False,
    keywords="pyqt5 qrc",
    classifiers=[
        "Topic :: Utilities",
        "Environment :: Console",
        "Development Status :: 4 - Beta"
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
