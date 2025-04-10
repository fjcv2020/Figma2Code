from setuptools import setup, find_packages

setup(
    name="figma_to_angular",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.30.0",
        "requests>=2.31.0",
        "openai>=1.12.0",
        "python-dotenv>=1.0.0",
        "tiktoken>=0.5.2",
        "pillow>=10.1.0",
        "numpy>=1.24.3",
        "msgpack>=1.0.7",
        "anthropic>=0.7.8",
    ],
    author="Tu Nombre",
    author_email="tu@email.com",
    description="Convierte diseños de Figma a código Angular",
    keywords="figma, angular, design, code generation, ai",
    url="https://github.com/tuusuario/figma-to-angular",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Designers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Code Generators",
    ],
    python_requires=">=3.7",
)