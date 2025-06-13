from builder import package_build

package_build.build_package(
    source=package_build.github_source(
        org='PrefectHQ',
        repo='prefect',
        tag='3.3.4'),
    setup_py_commands=['bdist_wheel'],
    build_dependencies=[]
)