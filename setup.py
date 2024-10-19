import setuptools

with open("requirements.txt") as open_file:
    install_requires = open_file.read()

setuptools.setup(
    name="Travel_Order_Resolver",
    description="Deuxieme projet d'IA d'Epitech : - NLP ",
    url_epitech="https://github.com/EpitechMscProPromo2025/T-AIA-901-PAR_22.git",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    python_requires=">=3.6",
)