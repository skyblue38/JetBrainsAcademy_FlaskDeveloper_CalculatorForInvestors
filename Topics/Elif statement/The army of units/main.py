size = int(input())
if size < 1:
    cohort = "no army"
elif size < 10:
    cohort = "few"
elif size < 50:
    cohort = "pack"
elif size < 500:
    cohort = "horde"
elif size < 1000:
    cohort = "swarm"
else:
    cohort = "legion"
print(cohort)
