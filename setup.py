from setuptools import setup, find_packages

setup(
    name="certbot-dns-sweb",
    version="1.0.0",
    description="Certbot DNS plugin for SpaceWeb official API",
    author="curserio",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "certbot>=2.0.0",
        "requests>=2.25.0"
    ],
    entry_points={
        "certbot.plugins": [
            "dns-sweb = certbot_dns_sweb.dns_sweb:Authenticator"
        ]
    },
)
