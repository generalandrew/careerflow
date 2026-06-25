#!/usr/bin/env node
/**
 * build_resume.js
 *
 * Renders an ATS-clean resume (.docx) from a tailored.json input.
 *
 * Usage:
 *   NODE_PATH=<workspace>/node_modules \
 *     node scripts/build_resume.js <tailored.json> <output.docx> [--conservative]
 *
 * tailored.json schema:
 * {
 *   "personal": { "name", "location", "phone", "email", "linkedin" },
 *   "headline": "Director, Solution Architecture | ...",
 *   "summary":  "...",
 *   "core_competencies": [ "..." , ... ],            // optional
 *   "roles": [ { "company", "title", "dates", "scope", "bullets": ["..."] }, ... ],
 *   "skills": { "Category": ["a","b"], ... },
 *   "education": [ { "school", "degree", "field" } ],
 *   "certifications": [ "..." ]
 * }
 *
 * --conservative: legacy ATS variant. Disables decorative borders + accent color,
 * collapses Core Competencies to single column, uses black text.
 */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, LevelFormat,
  BorderStyle, HeadingLevel, TabStopType, TabStopPosition,
} = require('docx');

// CLI parsing
const argv = process.argv.slice(2);
const flagConservative = argv.includes("--conservative");
const positional = argv.filter(a => !a.startsWith("--"));
const [inPath, outPath] = positional;
if (!inPath || !outPath) {
  console.error("Usage: build_resume.js <tailored.json> <output.docx> [--conservative]");
  process.exit(2);
}
const data = JSON.parse(fs.readFileSync(inPath, 'utf8'));

const FONT = "Calibri";
const accent = flagConservative ? "000000" : "1F3864";

// ATS v1.1 sanitizer:
//   - Date ranges with dashes preserved (Mar 2021 - Apr 2023)
//   - Email: / Phone: / LinkedIn: labels preserved
//   - Other dashes, colons, semicolons normalized to natural language
const sanitize = (s) => {
  if (typeof s !== "string") return s;
  const placeholders = [];
  const protect = (pattern) => {
    s = s.replace(pattern, (m) => {
      const key = `__P${placeholders.length}__`;
      placeholders.push(m);
      return key;
    });
  };
  protect(/\b\d{3}-\d{3}-\d{4}\b/g);            // phone numbers
  protect(/\b\d{5}-\d{4}\b/g);                   // US ZIP+4
  // Date ranges (Mar 2021 - Apr 2023, January 2024 - Present)
  protect(/\b[A-Z][a-z]{2,9}\s+\d{4}\s*-\s*(?:[A-Z][a-z]{2,9}\s+\d{4}|Present|present|Current|current)\b/g);
  // Labelled contact fields
  protect(/\b(Email|Phone|LinkedIn):/g);
  let out = s
    .replace(/—/g, " ")
    .replace(/–/g, " to ")
    .replace(/(\$\d+(?:\.\d+)?[KMB]?\+?)\s*-\s*(\$?\d+(?:\.\d+)?[KMB]?\+?)/g, "$1 to $2")
    .replace(/(\d+)\s*-\s*(\d+)(\s*(?:%|years?|yrs?|months?|weeks?|days?|hours?|hrs?|x|FTE|seats?))/gi, "$1 to $2$3")
    .replace(/([A-Za-z])-([A-Za-z])/g, "$1 $2")
    .replace(/\s-\s/g, " ")
    .replace(/-/g, " ")
    .replace(/:/g, "")
    .replace(/;/g, ",")
    .replace(/[ \t]{2,}/g, " ");
  placeholders.forEach((v, i) => { out = out.replace(`__P${i}__`, v); });
  return out;
};
const run = (text, opts = {}) => new TextRun({ text: sanitize(text), font: FONT, ...opts });
const para = (children, opts = {}) => new Paragraph({ children, ...opts });

const sectionHeader = (text) => {
  const opts = {
    spacing: { before: 120, after: 30 },
    children: [run(text, { bold: true, size: 22, color: accent, allCaps: true })],
  };
  if (!flagConservative) {
    opts.border = { bottom: { style: BorderStyle.SINGLE, size: 6, color: accent, space: 1 } };
  }
  return new Paragraph(opts);
};

const bullet = (text) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  spacing: { before: 0, after: 10 },
  children: [run(text, { size: 20 })]
});

// Header (name + contact line)
const headerName = new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 60 },
  children: [run(data.personal.name, { bold: true, size: 36, color: accent })]
});

// Contact line: Location | Phone: ... | Email: ... | LinkedIn URL
// Location is read from data.personal.location, falls back to omit if empty
const contactParts = [];
if (data.personal.location) contactParts.push(data.personal.location);
if (data.personal.phone)    contactParts.push(`Phone: ${data.personal.phone}`);
if (data.personal.email)    contactParts.push(`Email: ${data.personal.email}`);
if (data.personal.linkedin) contactParts.push(data.personal.linkedin);
const headerContact = new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 80 },
  children: [run(contactParts.join("  |  "), { size: 20, color: flagConservative ? "000000" : "595959" })]
});

const headerHeadline = data.headline ? new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 160 },
  children: [run(data.headline, { bold: true, size: 22 })]
}) : null;

const children = [headerName, headerContact];
if (headerHeadline) children.push(headerHeadline);

// SUMMARY
if (data.summary) {
  children.push(sectionHeader("Summary"));
  children.push(new Paragraph({
    spacing: { after: 60 },
    children: [run(data.summary, { size: 20 })]
  }));
}

// CORE COMPETENCIES (2-col standard, single col conservative)
if (data.core_competencies && data.core_competencies.length) {
  children.push(sectionHeader("Core Competencies"));
  const cols = data.core_competencies;
  if (flagConservative) {
    for (const item of cols) {
      children.push(bullet(item));
    }
  } else {
    const half = Math.ceil(cols.length / 2);
    const left = cols.slice(0, half);
    const right = cols.slice(half);
    for (let i = 0; i < half; i++) {
      const l = left[i] || "";
      const r = right[i] || "";
      children.push(new Paragraph({
        spacing: { after: 10 },
        tabStops: [{ type: TabStopType.LEFT, position: 4680 }],
        children: [
          run("•  " + l, { size: 20 }),
          run("\t" + (r ? "•  " + r : ""), { size: 20 })
        ]
      }));
    }
  }
}

// PROFESSIONAL EXPERIENCE
if (data.roles && data.roles.length) {
  children.push(sectionHeader("Professional Experience"));
  for (const role of data.roles) {
    const companyHeader = role.company + (role.client ? ` (Client: ${role.client})` : "");
    const headerRight = role.tenures ? "" : (role.dates || "");
    children.push(new Paragraph({
      spacing: { before: 80, after: 10 },
      tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
      children: [
        run(role.tenures ? companyHeader : `${role.title}, ${companyHeader}`, { bold: true, size: 21 }),
        run("\t" + headerRight, { size: 19, color: "595959" })
      ]
    }));

    if (role.tenures) {
      for (const t of role.tenures) {
        children.push(new Paragraph({
          spacing: { after: 0 },
          tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
          children: [
            run(t.title, { bold: true, italics: true, size: 20 }),
            run("\t" + (t.dates || ""), { italics: true, size: 19, color: "595959" })
          ]
        }));
      }
    }

    if (role.scope) {
      children.push(new Paragraph({
        spacing: { before: 40, after: 20 },
        children: [run(role.scope, { italics: true, size: 19, color: "595959" })]
      }));
    }
    for (const b of (role.bullets || [])) {
      children.push(bullet(typeof b === "string" ? b : b.text));
    }
  }
}

// SKILLS
if (data.skills && Object.keys(data.skills).length) {
  children.push(sectionHeader("Technical Skills"));
  for (const [cat, items] of Object.entries(data.skills)) {
    if (!items || !items.length) continue;
    children.push(new Paragraph({
      spacing: { after: 20 },
      children: [
        run(cat + "  ", { bold: true, size: 20 }),
        run(items.join(", "), { size: 20 })
      ]
    }));
  }
}

// EDUCATION (+ inline CERTIFICATIONS when small)
const certs = data.certifications || [];
const inlineCerts = certs.length > 0 && certs.length <= 2;
if (data.education && data.education.length) {
  children.push(sectionHeader(inlineCerts ? "Education & Certifications" : "Education"));
  for (const e of data.education) {
    const line = [e.degree, e.field].filter(Boolean).join(", ") + (e.school ? ", " + e.school : "");
    children.push(new Paragraph({
      spacing: { after: 20 },
      children: [run(line, { size: 20 })]
    }));
  }
  if (inlineCerts) {
    children.push(new Paragraph({
      spacing: { after: 20 },
      children: [
        run("Certifications  ", { bold: true, size: 20 }),
        run(certs.join(", "), { size: 20 })
      ]
    }));
  }
}

if (!inlineCerts && certs.length) {
  children.push(sectionHeader("Certifications"));
  for (const c of certs) {
    children.push(bullet(c));
  }
}

const doc = new Document({
  creator: data.personal.name || "careerflow",
  title: "Resume",
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } }
  },
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 360, hanging: 240 } } }
      }]
    }]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 720, right: 900, bottom: 720, left: 900 }
      }
    },
    children
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, buf);
  console.log("Wrote", outPath);
});
