for %%f in (Test-*.inp) do (
    echo "Running " %%f
    abaqus job=%%f user=UVARM4
)
