import React, { useState } from "react";

const ModalWithTabs = ({ isOpen, onClose, data }) => {
  if (!Object.keys(data).length) {
    return null;
  }

  const tabInit = {
    explanation: {
      val: (
        <>
          <p
            dangerouslySetInnerHTML={{
              __html: data.explanation.replace(/(?:\r\n|\r|\n)/g, "<br>"),
            }}
          />
        </>
      ),
    },
    contradictions: {
      val: <p>Contradiction exists: {data.contradiction}</p>,
    },
    similarity: {
      val: (
        <>
          <p>
            Similarity between ground truth and LLM output:{" "}
            <span className="font-semibold">
              {data.ground_truth_similarity}
            </span>
          </p>
          <p className="font-bold mt-4">Token Comparison: </p>
          <p>
            Token Correctness percentage:{" "}
            <span className="font-semibold">
              {data.token_correct_percentage}
            </span>
          </p>
          <div className="flex flex-wrap py-4">
            {data.token_comparison.map((item, index) => (
              <div
                key={index}
                className={`m-2 px-4 py-2 rounded-md text-white shadow-md ${
                  item.status ? "bg-green-500" : "bg-red-500"
                }`}
              >
                <p>{item.token}</p>
              </div>
            ))}
          </div>
        </>
      ),
    },
  };

  console.log(tabInit);

  // eslint-disable-next-line react-hooks/rules-of-hooks
  const [activeTab, setActiveTab] = useState(Object.keys(tabInit)[0]);

  const handleTabClick = (tabName: string) => {
    setActiveTab(tabName);
  };

  return !isOpen ? null : (
    <div className="fixed inset-0 flex items-center justify-center z-50 bg-gray-500 bg-opacity-50">
      <div className="bg-white rounded-lg shadow-lg max-w-4xl w-full p-6">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold">Results</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            &times;
          </button>
        </div>

        <div className="mt-4">
          <div className="flex space-x-4">
            {Object.keys(tabInit).map((tab) => (
              <button
                key={tab}
                onClick={() => handleTabClick(tab)}
                className={`tab px-4 py-2 font-semibold capitalize ${
                  activeTab === tab
                    ? "text-blue-500 border-b-2 border-blue-500"
                    : "text-gray-500"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div id="tab-content" className="mt-4">
            {Object.entries(tabInit).map(([key, value]) => (
              <div
                key={key}
                className={`tab-content ${
                  activeTab === key ? "block" : "hidden"
                }`}
              >
                {value.val}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModalWithTabs;
