# %% [markdown]
# # LLM-agent experiments on Kaggle (Ollama) - protocol amendment 3
#
# These are the real runs on TEST scenarios. Do not change anything except `RUNS` below.
#
# Before running:
# 1. Settings -> Internet: **On**. Accelerator: **GPU T4 x2**.
# 2. Add Input -> the dataset made from the latest `project_bundle.zip` (and only that one).
# 3. Set `RUNS` (one session each, in this order):
#    - session 1: `["pharma_llm_main"]`            (about 8 hours)
#    - session 2: `["energy_llm_main"]`            (about 8 hours)
#    - session 3: `["pharma_llm_adversarial", "energy_llm_adversarial"]`  (about 6 hours)
# 4. Click **Save Version -> Save & Run All (Commit)**. Do NOT use Run All in the editor:
#    an open editor session stops when it is idle. A committed version keeps running with
#    the browser closed.
# 5. When the version has finished, open it, go to **Output**, download
#    `llm_results.zip` and give it to Claude Code.

# %%
# SUSPENDED 2026-10-11: protocol amendment 3 is on hold (see docs/research_protocol.md).
# This notebook runs the suspended design on TEST scenarios and must not be run until a new
# amendment is approved.
raise SystemExit("Suspended: do not run. Use llm_pilot_kaggle.ipynb (pilot 4) instead.")

# %%
RUNS = ["pharma_llm_main"]
MODEL = "qwen2.5:7b"        # frozen in the protocol; a different model is refused
PARALLEL = 5

# %%
import glob
import json
import os
import shutil
import subprocess
import time
import zipfile

bundles = glob.glob("/kaggle/input/**/project_bundle.zip", recursive=True)
unpacked = glob.glob("/kaggle/input/**/run_experiment.py", recursive=True)
assert bundles or unpacked, "Attach the dataset made from project_bundle.zip (Add Input)."
assert len(unpacked) <= 1, "More than one project dataset is attached; keep only the latest."
WORK = "/kaggle/working/project"
shutil.rmtree(WORK, ignore_errors=True)
if unpacked:
    shutil.copytree(os.path.dirname(unpacked[0]), WORK)
else:
    with zipfile.ZipFile(bundles[0]) as archive:
        archive.extractall(WORK)
os.chdir(WORK)
assert os.path.exists("experiments/llm_runs.py"), "This dataset is an old bundle."
for run in RUNS:
    assert os.path.exists(f"configs/{run}.yaml"), f"unknown run {run!r}"

# %%
subprocess.run("apt-get install -y -qq zstd pciutils > /dev/null 2>&1", shell=True)
# the download server sometimes answers 504; retry instead of failing on the first error
for attempt in range(6):
    subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True)
    if shutil.which("ollama"):
        break
    print(f"Ollama install failed (attempt {attempt + 1} of 6); retrying in 60 s")
    time.sleep(60)
assert shutil.which("ollama"), "Ollama could not be installed; run this cell again later."
server = subprocess.Popen(["ollama", "serve"], stdout=open("/kaggle/working/ollama.log", "w"),
                          stderr=subprocess.STDOUT,
                          env={**os.environ, "OLLAMA_NUM_PARALLEL": str(PARALLEL)})
time.sleep(8)
subprocess.run(["ollama", "pull", MODEL], check=True)
print(subprocess.run(["ollama", "list"], capture_output=True, text=True).stdout)

# %%
# Energy gate (protocol A3.2): the model has never been tried on energy prompts. Ten rounds
# on energy VALIDATION scenarios must pass the pilot checks, or no energy run starts.
gate_ok = True
if any(run.startswith("energy") for run in RUNS):
    subprocess.run(["python", "-m", "experiments.llm_pilot", "--domain", "energy",
                    "--model", MODEL, "--rounds", "10", "--workers", str(PARALLEL),
                    "--tag", "_gate", "--output-dir", "results/pilot/energy_gate"], check=True)
    gate = json.load(open(glob.glob("results/pilot/energy_gate/*.json")[0]))
    checks = [v for system in gate["sanity_checks"].values() for v in system.values()]
    gate_ok = all(v is not False for v in checks)
    print("ENERGY GATE", "PASSED" if gate_ok else "FAILED", gate["sanity_checks"])

# %%
# Results are written seed by seed; a failure is reported at the end, after everything that
# did finish has been packed, so that completed seeds are never lost.
failures = []
for run in RUNS:
    if run.startswith("energy") and not gate_ok:
        failures.append(f"{run}: not started, energy gate failed")
        continue
    started = time.time()
    done = subprocess.run(["python", "run_experiment.py", "--config", f"configs/{run}.yaml",
                           "--resume"])
    print(f"{run}: exit {done.returncode} after {(time.time() - started) / 3600:.2f} h")
    if done.returncode != 0:
        failures.append(f"{run}: exit {done.returncode}")

# %%
out = "/kaggle/working/llm_results"
shutil.rmtree(out, ignore_errors=True)
os.makedirs(out)
for folder in glob.glob("results/raw/*_llm_*") + glob.glob("results/pilot/energy_gate"):
    shutil.copytree(folder, os.path.join(out, os.path.basename(folder)))
shutil.copy("/kaggle/working/ollama.log", os.path.join(out, "ollama.log"))
shutil.make_archive(out, "zip", out)
print("Download /kaggle/working/llm_results.zip from the Output tab of this version.")
print("FAILURES:", failures if failures else "none")
