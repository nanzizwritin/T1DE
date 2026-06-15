
# Diabetes Record Management System

An OCR-based data capture and analysis platform for Type 1 diabetes clinics. It turns photographed paper diabetes records into structured digital data, validates and stores them, runs automated clinical analysis, and presents the results through dedicated portals for healthcare professionals and for patients and families.

## Overview

Managing Type 1 diabetes generates a large volume of routine data — blood-glucose readings, insulin doses, diet, activity, and growth measurements. In many clinics this data is recorded on paper, and staff spend significant time reading those records and copying values into registers or spreadsheets before any analysis can happen.

This system removes that clerical step. A photograph of a standard record table is read automatically, the extracted values are checked and stored, and the data is turned into clear summaries and trend visualisations — freeing clinical time for patient care.

## The Problem It Addresses

Manual processing of paper diabetes records creates four recurring issues:

- **Time cost** — staff spend hours transcribing and tabulating data that could be captured automatically.
- **Accuracy** — hand-copying numbers introduces transcription errors.
- **Accessibility** — historical values are locked inside paper files, making it slow to retrieve a patient's trend over time.
- **Limited analysis** — without digital data, computing trends, flagging dangerous patterns, and generating reports is difficult.

## What It Does

- **Photo capture** of a standard diabetes record table via uploaded images.
- **Image pre-processing** — checks for blur, lighting, and cropping, and corrects orientation so OCR is reliable in everyday clinic conditions.
- **OCR extraction** that converts the record table into digital values.
- **Confidence-based validation** — values read with high confidence are accepted automatically; uncertain values are flagged for review rather than stored as fact.
- **Structured storage** of patient information, centre information, extracted values, and the original image together, so any number can be traced back to its source.
- **Automated analysis** — glucose trends over time, total daily insulin dose and comparison across visits, frequency of out-of-range readings, and height/weight tracking.
- **Reports and visual summaries**, including trend charts, with PDF export.
- **Two portals** — one for healthcare professionals to capture, review, and confirm records, and one for patients and families to view their history and enter daily values.

## How It Works

The system is organised as a pipeline of independent modules:

```
Image capture → Pre-processing → OCR → Confidence & validation
        → Database → Analysis → Portals
```

Authentication wraps the whole system so that each user sees only the records they are permitted to access. Values are stored only after they pass confidence checks or are corrected during review, keeping the database trustworthy.

## Technology Stack

| Layer | Tool |
| --- | --- |
| Core language | Python |
| Image pre-processing | OpenCV |
| OCR engine | PaddleOCR |
| Database | SQLite |
| Web portal | Streamlit |
| Analysis & charts | pandas, Matplotlib |
| PDF reports | ReportLab |
| Version control | Git |

## Data Privacy & Ethics

Because the system handles the health data of children, privacy is treated as a design requirement:

- **Minimisation & de-identification** — records are keyed by centre and child identifiers rather than by name wherever possible.
- **Access control** — authentication ensures staff and families see only the records they are authorised to view.
- **Source traceability** — the original image is stored alongside extracted values so any number can be audited against its source.
- **Consent** — designed to operate only on records collected with appropriate consent, in line with India's Digital Personal Data Protection Act, 2023.
- **Scope limit** — the system summarises data to assist clinicians; it does not make diagnoses or treatment decisions.

## Author

Nandini Singla