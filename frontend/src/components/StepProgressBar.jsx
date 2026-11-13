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
      title: "Dietary Profile",
      desc: "Preferences & Allergens",
      icon: "leaf",
      isReady: true
    },
    {
      num: 3,
      title: "Product Scan",
      desc: "Photo, Image or Text",
      icon: "camera",
      isReady: true
    },
    {
      num: 4,
      title: "Personalised Results",
      desc: "Suitability & Safety",
      icon: "shieldCheck",
      isReady: currentStep >= 4
    }
  ];

  return (
    <div className="stepper-container">
      <div className="stepper-track">
        {steps.map((s, idx) => {
          const isCompleted = currentStep > s.num;
          const isActive = currentStep === s.num;
          const isClickable = s.num <= currentStep || (s.num === 1) || (s.num === 2) || (s.num === 3);

          return (
            <React.Fragment key={s.num}>
              <button
                type="button"
                className={`step-item ${isActive ? "active" : ""} ${isCompleted ? "completed" : ""}`}
                onClick={() => isClickable && onSelectStep(s.num)}
                disabled={!isClickable}
                aria-current={isActive ? "step" : undefined}
              >
                <div className="step-circle">
                  {isCompleted ? (
                    <Icon name="check" size={16} strokeWidth={2.5} color="#ffffff" />
                  ) : (
                    <span>{s.num}</span>
                  )}
                </div>
                <div className="step-content">
                  <span className="step-title">{s.title}</span>
                  <span className="step-desc">{s.desc}</span>
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
