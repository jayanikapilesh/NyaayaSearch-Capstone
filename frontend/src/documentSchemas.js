// Each document type defines its own form schema: sections, fields, labels, and types.
// This drives both the dynamic form AND the values sent to the backend.

export const DOCUMENT_SCHEMAS = {
  rent_agreement: {
    label: "Rent Agreement",
    sections: [
      {
        title: "Landlord Details",
        fields: [
          { key: "landlord_name", label: "Landlord Name", type: "text", placeholder: "Enter landlord's full name" },
          { key: "landlord_address", label: "Landlord Address", type: "textarea", placeholder: "Enter landlord's address" },
        ],
      },
      {
        title: "Tenant Details",
        fields: [
          { key: "tenant_name", label: "Tenant Name", type: "text", placeholder: "Enter tenant's full name" },
          { key: "tenant_address", label: "Tenant Address", type: "textarea", placeholder: "Enter tenant's address" },
        ],
      },
      {
        title: "Property Details",
        fields: [
          { key: "property_address", label: "Property Address", type: "textarea", placeholder: "Enter rental property address" },
          { key: "property_type", label: "Property Type", type: "select", options: ["Apartment", "House", "Room", "Other"] },
        ],
      },
      {
        title: "Rent Details",
        fields: [
          { key: "monthly_rent", label: "Monthly Rent (Rs.)", type: "number", placeholder: "Enter amount" },
          { key: "security_deposit", label: "Security Deposit (Rs.)", type: "number", placeholder: "Enter amount" },
          { key: "start_date", label: "Agreement Start Date", type: "date" },
          { key: "end_date", label: "Agreement End Date", type: "date" },
          { key: "notice_period", label: "Notice Period (days)", type: "text", placeholder: "e.g. 30" },
        ],
      },
    ],
  },

  affidavit: {
    label: "Affidavit",
    sections: [
      {
        title: "Deponent Details",
        fields: [
          { key: "deponent_name", label: "Your Full Name", type: "text", placeholder: "Enter your full name" },
          { key: "deponent_address", label: "Your Address", type: "textarea", placeholder: "Enter your address" },
          { key: "deponent_age", label: "Your Age", type: "text", placeholder: "Enter your age" },
        ],
      },
      {
        title: "Affidavit Details",
        fields: [
          { key: "purpose", label: "Purpose of Affidavit", type: "textarea", placeholder: "What is this affidavit for? (e.g. name correction, address proof)" },
          { key: "statement", label: "Statement / Facts to Declare", type: "textarea", placeholder: "Briefly describe what you are swearing to" },
        ],
      },
    ],
  },

  job_offer: {
    label: "Job Offer Letter",
    sections: [
      {
        title: "Company Details",
        fields: [
          { key: "company_name", label: "Company Name", type: "text", placeholder: "Enter company name" },
          { key: "company_address", label: "Company Address", type: "textarea", placeholder: "Enter company address" },
        ],
      },
      {
        title: "Candidate Details",
        fields: [
          { key: "candidate_name", label: "Candidate Name", type: "text", placeholder: "Enter candidate's full name" },
          { key: "job_title", label: "Job Title", type: "text", placeholder: "Enter job title/designation" },
        ],
      },
      {
        title: "Offer Details",
        fields: [
          { key: "joining_date", label: "Joining Date", type: "date" },
          { key: "salary", label: "Annual Salary (Rs.)", type: "number", placeholder: "Enter annual CTC" },
          { key: "work_location", label: "Work Location", type: "text", placeholder: "Enter work location" },
          { key: "employment_type", label: "Employment Type", type: "select", options: ["Full-time", "Part-time", "Contract", "Internship"] },
        ],
      },
    ],
  },

  divorce_petition: {
    label: "Divorce Petition",
    sections: [
      {
        title: "Petitioner Details",
        fields: [
          { key: "petitioner_name", label: "Your Name (Petitioner)", type: "text", placeholder: "Enter your full name" },
          { key: "petitioner_address", label: "Your Address", type: "textarea", placeholder: "Enter your address" },
        ],
      },
      {
        title: "Respondent Details",
        fields: [
          { key: "respondent_name", label: "Spouse's Name (Respondent)", type: "text", placeholder: "Enter spouse's full name" },
          { key: "respondent_address", label: "Spouse's Address", type: "textarea", placeholder: "Enter spouse's address" },
        ],
      },
      {
        title: "Marriage Details",
        fields: [
          { key: "marriage_date", label: "Date of Marriage", type: "date" },
          { key: "marriage_place", label: "Place of Marriage", type: "text", placeholder: "Enter place of marriage" },
          { key: "grounds", label: "Grounds for Divorce", type: "textarea", placeholder: "Briefly describe the grounds (e.g. mutual consent)" },
        ],
      },
    ],
  },
};

// Document types without a detailed schema yet - fall back to a simple free-text form
export const GENERIC_DOCUMENT_TYPES = {
  legal_notice: "Legal Notice",
  power_of_attorney: "Power of Attorney",
  noc: "No Objection Certificate (NOC)",
  will: "Will",
  partnership_deed: "Partnership Deed",
};
