import React from "react";
import Icon from "./Icons";

export default function StepProgressBar({ currentStep, onSelectStep, currentUser }) {
  const steps = [
    {
      num: 1,
      title: "Account",
      desc: currentUser ? currentUser.username : "Sign In / Register",
      icon: "user",
      isReady: true
    },
    {
      num: 2,
      title: "Allergies",
      desc: "Configure Sensitivities",
      icon: "shieldAlert",
      isReady: true
    },
    {
      num: 3,
      title: "Preferences",
      desc: "Dietary & Additives",
      icon: "leaf",
      isReady: true
    },
    {
      num: 4,
      title: "Product Scan",
      desc: "Photo, Image or Code",
      icon: "camera",
      isReady: true
    },
    {
      num: 5,
      title: "Results",
      desc: "Personalised Analysis",
      icon: "shieldCheck",
      isReady: currentStep >= 5
    }
  ];

  return (
    <div className="stepper-container">
      <div className="stepper-track">
        {steps.map((s, idx) => {
          const isCompleted = currentStep > s.num;
          const isActive = currentStep === s.num;
          const isClickable = s.num <= currentStep || (s.num <= 4);

          return (
            <React.Fragment key={s.num}>
              <button
                type="button"
                className={`step-item ${isActive ? "active" : ""} ${isCompleted ? "completed" : ""}`}
                onClick={() => isClickable && onSelectStep(s.num)}
                disabled={!isClickable}
                aria-current={isActive ? "step" : undefined}
                title={`Navigate to Step ${s.num}: ${s.title}`}
              >
                <div className="step-circle">
                  {isCompleted ? (
                    <Icon name="check" size={15} strokeWidth={2.5} color="#ffffff" />
                  ) : (
                    <span>{s.num}</span>
                  )}
                </div>
                <div className="step-content">
                  <span className="step-title">{s.title}</span>
                </div>
              </button>

              {idx < steps.length - 1 && (
                <div className={`step-connector ${currentStep > s.num ? "completed" : ""}`} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
