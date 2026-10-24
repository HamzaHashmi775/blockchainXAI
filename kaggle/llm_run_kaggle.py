# %% [markdown]
# # LLM-agent experiments on Kaggle (Ollama) - protocol amendments 4, 6, 7 and 8
#
# These are the real runs on TEST scenarios. Do not change anything except `RUNS` below.
#
# Before running:
# 1. Settings -> Internet: **On**. Accelerator: **GPU T4 x2**.
# 2. Add Input -> the dataset made from the latest `project_bundle.zip` (and only that one).
# 3. Set `RUNS` (one session each, in this order):
#    - session 1: `["pharma_llm_main"]`        (about 8.6 hours)
#    - session 2: `["energy_llm_main"]`        (about 8.6 hours)
#    - session 3: `["pharma_llm_main_w075"]`   (about 9.2 hours)
#    - session 4: `["pharma_llm_adversarial", "energy_llm_adversarial"]`  (about 9.5 hours)
#    - session 5 (amendment 6, prompt-only control): `["pharma_llm_prompt_control"]`
#      (about 8.3 hours)
#    - session 6 (amendment 7, condition D): `["pharma_llm_prompt_control_d"]`
#      (about 3 hours)
#    - session 7 (amendment 8, energy A-C): `["energy_llm_prompt_control"]`  (about 8.6 hours)
#    - session 8 (amendment 8, energy D): `["energy_llm_prompt_control_d"]`  (about 3 hours)
#    The notebook stops at once if no GPU is attached (session 6 first ran on a CPU and
#    produced nothing).
# 4. Click **Save Version -> Save & Run All (Commit)**. Do NOT use Run All in the editor:
#    an open editor session stops when it is idle. A committed version keeps running with
#    the browser closed.
# 5. When the version has finished, open it, go to **Output**, download
#    `llm_results.zip` and give it to Claude Code.

# %%
RUNS = ["energy_llm_prompt_control"]
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
assert os.path.exists("configs/energy_llm_prompt_control_d.yaml"), "This dataset is an old bundle."
for run in RUNS:
    assert os.path.exists(f"configs/{run}.yaml"), f"unknown run {run!r}"

# %%
# without a GPU every model call times out after 10 min and nothing is saved
gpu = subprocess.run("nvidia-smi -L", shell=True, capture_output=True, text=True)
print(gpu.stdout)
assert gpu.returncode == 0 and "GPU" in gpu.stdout, (
    "No GPU found: set Settings -> Accelerator -> GPU T4 x2, then save and run again.")
subprocess.run("apt-get install -y -qq zstd pciutils > /dev/null 2>&1", shell=True)
# the download server sometimes answers 504; retry instead of failing on the first error
for attempt in range(6):
    subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True)
    if shutil.which("ollama"):
        break
    print(f"Ollama install failed (attempt {attempt + 1} of 6); retrying in 60 s")
    time.sleep(60)
assert shutil.which("ollama"), "Ollama could not be installed; run this cell again later."
server = subprocess.Popen(["ollama", "serve"], stdout=open("/tmp/ollama.log", "w"),
                          stderr=subprocess.STDOUT,
                          env={**os.environ, "OLLAMA_NUM_PARALLEL": str(PARALLEL)})
time.sleep(8)
subprocess.run(["ollama", "pull", MODEL], check=True)
print(subprocess.run(["ollama", "list"], capture_output=True, text=True).stdout)

# %%
# Results are written seed by seed; a failure is reported at the end, after everything that
# did finish has been packed, so that completed seeds are never lost.
failures = []
for run in RUNS:
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
for folder in glob.glob("results/raw/*_llm_*"):
    shutil.copytree(folder, os.path.join(out, os.path.basename(folder)))
# the server log grows by about 65 kB per model call, so only its two ends are kept
with open("/tmp/ollama.log", errors="replace") as log:
    lines = log.readlines()
with open(os.path.join(out, "ollama_log_excerpt.txt"), "w") as excerpt:
    excerpt.writelines(lines[:300] + ["... (cut) ...\n"] + lines[-300:])
shutil.make_archive(out, "zip", out)
print("Download /kaggle/working/llm_results.zip from the Output tab of this version.")
print("FAILURES:", failures if failures else "none")
