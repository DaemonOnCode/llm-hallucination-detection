"use client";
import Dropdown from "@/components/dropdown";
import ModalWithTabs from "@/components/modal";
import { GenerationType } from "@/utils/constants";
import { useRef, useState } from "react";

export default function Home() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const promptRef = useRef<HTMLTextAreaElement>(null);
  const answerRef = useRef<HTMLTextAreaElement>(null);
  const groundTruthRef = useRef<HTMLTextAreaElement>(null);

  const [isModalOpen, setModalOpen] = useState<boolean>(false);
  const [contextState, setContextState] = useState<string>("");
  const [modelTypeState, setModelTypeState] = useState<string>("");
  const [keyState, setKeyState] = useState<string>("");
  const [resultData, setResultData] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState<boolean>(false);

  const [generationType, setGenerationType] =
    useState<keyof typeof GenerationType>("generated");

  const onFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    console.log("Form submitted", e.target);

    const formData = new FormData();
    if (promptRef.current?.value === "" || !promptRef.current?.value) {
      alert("Prompt/Input field is required");
      setLoading(false);
      return;
    }
    formData.append("prompt", promptRef.current.value);
    formData.append("answer", answerRef.current?.value || "");
    formData.append("ground_truth", groundTruthRef.current?.value || "");
    formData.append("context", contextState || "");
    if (answerRef.current?.value === "") {
      formData.append("api_key", keyState || "");
      let modelType = modelTypeState;
      if (modelTypeState.search("/") !== -1) {
        modelType = "hf_" + modelType;
      } else if (keyState !== "") {
        modelType = "openai_" + modelType;
      } else {
        modelType = "ollama_" + modelType;
      }
      formData.append("model_type", modelType || "");
    }
    for (const file of fileInputRef.current?.files || []) {
      formData.append(file.name, file);
    }

    console.log("Form data", [...formData.entries()]);

    try {
      const res = await fetch("http://localhost:5000/api/process", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      console.log(data);

      setResultData(data);
      setModalOpen(true);
    } catch (e) {
      console.log(e);
    }

    setLoading(false);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div>
        <div className="flex items-center justify-center my-12">
          <Dropdown
            options={Object.keys(GenerationType)}
            changeGenerationType={(e) => setGenerationType(e)}
            generationType={generationType}
          />
        </div>
        <div className="bg-white p-6">
          <div className="mb-4">
            <h2 className="text-xl font-bold">Check Hallucinations</h2>
            <p className="text-gray-600">
              Enter the prompt, answer, ground truth to check for
              hallucinations.
            </p>
          </div>
          <form className="flex flex-col gap-y-4" onSubmit={onFormSubmit}>
            <textarea
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 p-2 text-sm"
              placeholder="Enter prompt sent to LLM"
              ref={promptRef}
            />
            {generationType === "generated" ? (
              <textarea
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 p-2 text-sm"
                placeholder="Enter answer output by the LLM"
                ref={answerRef}
              />
            ) : (
              <></>
            )}
            <div className="flex flex-row gap-x-4">
              <textarea
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 p-2 text-sm"
                placeholder="Enter ground truth value (your facts and data)"
                ref={groundTruthRef}
              />
              <input
                className="flex h-10 w-full rounded-md border border-input bg-background ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 p-2 text-sm cursor-pointer"
                placeholder="Upload ground truth files (Optional)"
                multiple={true}
                accept=".txt,.pdf,.doc,.docx"
                type="file"
                ref={fileInputRef}
              />
            </div>
            {generationType === "to_generate" ? (
              <>
                <input
                  className="flex h-10 w-full rounded-md border border-input bg-background ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 p-2 text-sm"
                  placeholder="Enter context, for e.g. this question is about geography and capitals"
                  value={contextState}
                  onChange={(e) => setContextState(e.target.value)}
                />
                <input
                  className="flex h-10 w-full rounded-md border border-input bg-background ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 p-2 text-sm"
                  placeholder="Enter LLM model to be used if not providing output"
                  value={modelTypeState}
                  onChange={(e) => setModelTypeState(e.target.value)}
                />
                <input
                  className="flex h-10 w-full rounded-md border border-input bg-background ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 p-2 text-sm"
                  placeholder="API Key for OpenAI"
                  value={keyState}
                  onChange={(e) => setKeyState(e.target.value)}
                />
              </>
            ) : (
              <></>
            )}
            <button
              className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 self-start"
              type="submit"
              disabled={loading}
            >
              {loading ? "Processing..." : "Submit"}
            </button>
          </form>
        </div>
        <ModalWithTabs
          isOpen={isModalOpen}
          onClose={() => setModalOpen(false)}
          data={resultData}
        />
      </div>
    </main>
  );
}
