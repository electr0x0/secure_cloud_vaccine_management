export const commonMedicalConditions = [
  { value: "diabetes", label: "Diabetes" },
  { value: "hypertension", label: "Hypertension" },
  { value: "asthma", label: "Asthma" },
  { value: "heart_disease", label: "Heart Disease" },
  { value: "thyroid", label: "Thyroid Disorder" },
  { value: "allergies", label: "Allergies" },
]

export const severityOptions = [
  { value: "mild", label: "Mild" },
  { value: "moderate", label: "Moderate" },
  { value: "severe", label: "Severe" }
]

export const userTypes = [
  { value: "1", label: "Vaccine Recipient" },
  { value: "2", label: "Vaccinator" }
]

export const identityValidationPatterns = {
  nid: /^(\d{10}|\d{17})$/,
  brn: /^\d{17}$/,
  passport: /^[A-Z]{2}\d{7}$/
}

