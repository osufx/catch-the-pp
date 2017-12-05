from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os

extensions = []
for root, dirs, files in os.walk(os.getcwd()):
    for file in files:
        if file.endswith(".pyx"):
            file_path = os.path.relpath(os.path.join(root, file))
            extensions.append(Extension(file_path.replace("/", ".")[:-4], [file_path]))

setup(
    name="catch-the-pp",
    ext_modules=cythonize(extensions, nthreads=4),
)
