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


export const ADDITIONAL_DOCUMENT_SCHEMAS = {
  legal_notice: {
    label: "Legal Notice",
    sections: [
      {
        title: "Sender Details",
        fields: [
          { key: "sender_name", label: "Your Name", type: "text", placeholder: "Enter your full name" },
          { key: "sender_address", label: "Your Address", type: "textarea", placeholder: "Enter your address" },
        ],
      },
      {
        title: "Recipient Details",
        fields: [
          { key: "recipient_name", label: "Recipient Name", type: "text", placeholder: "Enter the recipient full name" },
          { key: "recipient_address", label: "Recipient Address", type: "textarea", placeholder: "Enter recipient address" },
        ],
      },
      {
        title: "Notice Details",
        fields: [
          { key: "subject", label: "Subject of Notice", type: "text", placeholder: "e.g. Non-payment of dues" },
          { key: "details", label: "Details / Facts", type: "textarea", placeholder: "Describe the issue and what happened" },
          { key: "demand", label: "What You Are Demanding", type: "textarea", placeholder: "e.g. Payment within 15 days" },
          { key: "response_deadline", label: "Response Deadline (days)", type: "text", placeholder: "e.g. 15" },
        ],
      },
    ],
  },

  power_of_attorney: {
    label: "Power of Attorney",
    sections: [
      {
        title: "Principal Details",
        fields: [
          { key: "principal_name", label: "Your Name (Principal)", type: "text", placeholder: "Enter your full name" },
          { key: "principal_address", label: "Your Address", type: "textarea", placeholder: "Enter your address" },
        ],
      },
      {
        title: "Attorney Details",
        fields: [
          { key: "attorney_name", label: "Attorney Name (Person You Are Authorizing)", type: "text", placeholder: "Enter their full name" },
          { key: "attorney_address", label: "Attorney Address", type: "textarea", placeholder: "Enter their address" },
        ],
      },
      {
        title: "Power Details",
        fields: [
          { key: "poa_type", label: "Type", type: "select", options: ["General", "Specific"] },
          { key: "powers_granted", label: "Powers Being Granted", type: "textarea", placeholder: "Describe what the attorney is authorized to do" },
          { key: "duration", label: "Duration / Validity", type: "text", placeholder: "e.g. Until revoked, or a specific date" },
        ],
      },
    ],
  },

  noc: {
    label: "No Objection Certificate (NOC)",
    sections: [
      {
        title: "Issuer Details",
        fields: [
          { key: "issuer_name", label: "Your Name (Issuing NOC)", type: "text", placeholder: "Enter your full name" },
          { key: "issuer_address", label: "Your Address", type: "textarea", placeholder: "Enter your address" },
        ],
      },
      {
        title: "Recipient Details",
        fields: [
          { key: "recipient_name", label: "Recipient Name", type: "text", placeholder: "Who is this NOC for?" },
        ],
      },
      {
        title: "NOC Details",
        fields: [
          { key: "purpose", label: "Purpose of NOC", type: "textarea", placeholder: "e.g. For opening a bank account, for a loan, for rental use" },
        ],
      },
    ],
  },

  will: {
    label: "Will",
    sections: [
      {
        title: "Testator Details",
        fields: [
          { key: "testator_name", label: "Your Name (Testator)", type: "text", placeholder: "Enter your full name" },
          { key: "testator_address", label: "Your Address", type: "textarea", placeholder: "Enter your address" },
          { key: "testator_age", label: "Your Age", type: "text", placeholder: "Enter your age" },
        ],
      },
      {
        title: "Executor Details",
        fields: [
          { key: "executor_name", label: "Executor Name", type: "text", placeholder: "Person who will carry out this will" },
        ],
      },
      {
        title: "Bequests",
        fields: [
          { key: "beneficiaries", label: "Beneficiaries and What They Receive", type: "textarea", placeholder: "List who receives what" },
        ],
      },
    ],
  },

  partnership_deed: {
    label: "Partnership Deed",
    sections: [
      {
        title: "Partner 1 Details",
        fields: [
          { key: "partner1_name", label: "Partner 1 Name", type: "text", placeholder: "Enter full name" },
          { key: "partner1_address", label: "Partner 1 Address", type: "textarea", placeholder: "Enter address" },
        ],
      },
      {
        title: "Partner 2 Details",
        fields: [
          { key: "partner2_name", label: "Partner 2 Name", type: "text", placeholder: "Enter full name" },
          { key: "partner2_address", label: "Partner 2 Address", type: "textarea", placeholder: "Enter address" },
        ],
      },
      {
        title: "Business Details",
        fields: [
          { key: "business_name", label: "Business Name", type: "text", placeholder: "Enter the firm/partnership name" },
          { key: "business_nature", label: "Nature of Business", type: "text", placeholder: "e.g. Retail trading, consultancy" },
          { key: "profit_sharing", label: "Profit Sharing Ratio", type: "text", placeholder: "e.g. 50:50" },
          { key: "capital_contribution", label: "Capital Contribution", type: "textarea", placeholder: "Describe each partner contribution" },
        ],
      },
    ],
  },
};
