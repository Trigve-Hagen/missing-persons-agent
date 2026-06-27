import os
import subprocess
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from classes.model_utils import ModelUtils

# Define the State representing the data flowing through our graph
class AudioAsrState(TypedDict):
    audio_path: str          # Path to the source input .wav file (Must be 24kHz)
    system_prompt: str       # Instruction given to the ASR model
    transcription: Optional[str] # The final output text extracted from the audio
    error: Optional[str]     # Captures any processing issues during execution


class LFMCpuAudioTransformer:
    def __init__(self, checkpoint_dir: str, binary_name: str = "llama-liquid-audio-cli.exe"):
        """
        Initializes the CPU execution paths for the LFM2.5 GGUF components.
        """
        self.binary = os.path.abspath(binary_name)

        abs_checkpoint = os.path.abspath(checkpoint_dir)
        self.model_path = os.path.join(abs_checkpoint, "LFM2.5-Audio-1.5B-Q4_0.gguf")
        self.mmproj_path = os.path.join(abs_checkpoint, "mmproj-LFM2.5-Audio-1.5B-Q4_0.gguf")
        self.vocoder_path = os.path.join(abs_checkpoint, "vocoder-LFM2.5-Audio-1.5B-Q4_0.gguf")
        self.tokenizer_path = os.path.join(abs_checkpoint, "tokenizer-LFM2.5-Audio-1.5B-Q4_0.gguf")

    def validate_inputs(self, state: AudioAsrState) -> AudioAsrState:
        """Node 1: Validates existence of files prior to compute resource allocation."""
        if not os.path.exists(state["audio_path"]):
            state["error"] = f"Audio target file missing at: {state['audio_path']}"
        elif not os.path.exists(self.model_path):
            state["error"] = f"LFM2.5 GGUF file missing at: {self.model_path}"
        return state

    def execute_asr(self, state: AudioAsrState) -> AudioAsrState:
        """Node 2: Runs CPU-bound inference utilizing llama-liquid-audio-cli."""
        if state.get("error"):
            return state

        # Construct the execution command mapping out standard LFM2.5 CPU architecture components
        command = [
            self.binary,
            "-m", self.model_path,
            "-mm", self.mmproj_path,
            "-mv", self.vocoder_path,
            "--tts-speaker-file", self.tokenizer_path,
            "-sys", state["system_prompt"],
            "--audio", os.path.abspath(state["audio_path"])
        ]

        try:
            # Trigger CPU execution and capture output stream natively
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                shell=True
            )

            # Clean up the output stream to return raw transcription text
            state["transcription"] = result.stdout.strip()

        except subprocess.CalledProcessError as e:
            state["error"] = f"Inference execution failed: {e.stderr}"

        return state


def router_condition(state: AudioAsrState) -> str:
    """Conditional Routing: Decides path based on error metrics."""
    if state.get("error"):
        return "failed_termination"
    return "successful_termination"


# --- Graph Construction Flow ---

# 1. Point toward your local directory housing your downloaded GGUF weights
WEIGHTS_DIR = ModelUtils.resource_path(os.path.join("assets", "models", "LFM2.5-Audio-1.5B-GGUF")) # "./models/LFM2.5-Audio-1.5B-GGUF"
transformer = LFMCpuAudioTransformer(checkpoint_dir=WEIGHTS_DIR)

# 2. Instantiate state graph workflow architecture
builder = StateGraph(AudioAsrState)

# 3. Add node definitions to the layout
builder.add_node("validate_inputs", transformer.validate_inputs)
builder.add_node("transcribe_audio", transformer.execute_asr)

# 4. Lay out the structural progression pathways
builder.add_edge(START, "validate_inputs")
builder.add_edge("validate_inputs", "transcribe_audio")

# 5. Route dynamic execution states safely out of the graph
builder.add_conditional_edges(
    "transcribe_audio",
    router_condition,
    {
        "successful_termination": END,
        "failed_termination": END
    }
)

# 6. Compile the operational state workflow
audio_pipeline = builder.compile()


# --- Execution Example ---
if __name__ == "__main__":
    # Ensure your target audio is downsampled/saved at 24000Hz mono per model requirement
    input_payload: AudioAsrState = {
        "audio_path": ModelUtils.resource_path(os.path.join("assets", "audio-samples", "barackobamafederalplaza.mp3")),
        "system_prompt": "Perform ASR.",
        "transcription": None,
        "error": None
    }

    print("--- Initializing CPU Inference Graph Flow ---")
    print(ModelUtils.resource_path(os.path.join("assets", "audio-samples", "barackobamafederalplaza.mp3")))
    final_output = audio_pipeline.invoke(input_payload)

    if final_output.get("error"):
        print(f"Workflow Stopped Early. Reason: {final_output['error']}")
    else:
        print("\n--- Transcription Successful ---")
        print(final_output["transcription"])
