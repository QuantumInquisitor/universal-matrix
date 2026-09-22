# Waters Legacy Trust Proprietary Commercial License Agreement

> **Template for legal review and negotiated execution.**
>
> This document is a complete commercial-license framework, but it is not
> effective until the parties complete the applicable schedules and execute the
> agreement. It should be reviewed by qualified counsel for the specific
> transaction, parties, jurisdiction, and regulated-use context.

This Proprietary Commercial License Agreement ("Agreement") is entered into as
of **[Effective Date]** by and between:

**Licensor:** Waters Legacy Trust, **[legal address and jurisdiction]**
("Licensor")

and

**Licensee:** **[full legal name, entity type, address, and jurisdiction]**
("Licensee").

Licensor and Licensee may each be a "Party" and together the "Parties."

## 1. Background

A. Licensor develops and manages the Universal Matrix software platform and
associated software modules, documentation, specifications, APIs, SDKs,
research tooling, spatial/robotics components, digital-twin components,
manufacturing components, edge/HAL components, and related materials.

B. Certain versions of Universal Matrix are also made available publicly under
the GNU Affero General Public License, version 3 or later ("AGPL").

C. Licensee desires rights under proprietary commercial terms that are
different from or additional to rights available under the public AGPL option.

D. Licensor is willing to grant such rights solely on the terms of this
Agreement and the attached schedules.

## 2. Definitions

### 2.1 "Licensed Software"

"Licensed Software" means only the Universal Matrix code, documentation, models,
schemas, interfaces, and other materials expressly identified in **Schedule A
(Licensed Scope)**.

Licensed Software may be identified by one or more of:

- repository path;
- product family;
- release version;
- Git tag;
- commit hash;
- package name;
- artifact digest;
- source archive;
- written module list.

No repository component is licensed commercially merely because it exists in
the same repository.

### 2.2 "Product Family"

A "Product Family" means one or more of the following commercial groupings when
listed in Schedule A:

- Universal Matrix Core
- Universal Matrix Spatial
- Universal Matrix Robotics
- Universal Matrix Manufacturing
- Universal Matrix Research
- Universal Matrix Edge
- Universal Matrix Enterprise

### 2.3 "Authorized Deployment"

"Authorized Deployment" means a deployment permitted by Schedule B, such as a
specified number of devices, sites, servers, tenants, users, facilities, OEM
units, or customer installations.

### 2.4 "Derivative Work"

"Derivative Work" means a modification or derivative of the Licensed Software
that requires copyright permission from Licensor under applicable law.

### 2.5 "Documentation"

"Documentation" means user guides, technical specifications, API definitions,
schemas, release notes, integration instructions, and similar materials
provided by Licensor for the Licensed Software.

### 2.6 "Confidential Information"

"Confidential Information" means nonpublic information disclosed by one Party
to the other and identified as confidential or that reasonably should be
understood to be confidential given the nature of the information and the
circumstances of disclosure.

### 2.7 "Third-Party Materials"

"Third-Party Materials" means software, data, models, standards content, assets,
libraries, dependencies, or other materials not owned or controlled by
Licensor.

## 3. Commercial License Grant

Subject to Licensee's payment of all applicable fees and continued compliance
with this Agreement, Licensor grants Licensee during the Term a limited,
non-exclusive, non-transferable except as expressly permitted, non-sublicensable
except as expressly permitted, proprietary license to use the Licensed Software
within the Licensed Scope and Authorized Deployment specified in the schedules.

The commercial license may include, only if expressly selected in Schedule A or
B, rights to:

1. install and execute the Licensed Software internally;
2. modify the Licensed Software for Licensee's internal use;
3. deploy the Licensed Software in private or public network services;
4. operate closed-source SaaS services using the Licensed Software;
5. embed the Licensed Software in proprietary applications;
6. embed the Licensed Software in hardware or OEM products;
7. distribute object-code copies to authorized customers;
8. distribute approved Derivative Works;
9. operate the Licensed Software for Licensee's customers;
10. create customer-specific integrations;
11. access source code under the confidentiality terms of this Agreement.

No right listed above applies unless the applicable schedule affirmatively
grants it.

## 4. Relationship to the Public AGPL License

### 4.1 Separate license paths

The public AGPL license and this proprietary Agreement are separate alternative
license paths.

A recipient may exercise rights under the AGPL if that recipient satisfies the
AGPL terms. A Licensee that enters this Agreement may instead exercise the
commercial rights expressly granted here for the Licensed Software.

### 4.2 No restriction of AGPL recipients

Nothing in this Agreement alters or restricts rights previously granted to any
recipient under a valid public AGPL license.

### 4.3 Commercial-license compliance

For Licensed Software used under this Agreement, the Parties intend this
Agreement to govern the proprietary rights granted by Licensor to Licensee,
rather than requiring Licensee to rely on the AGPL grant for that same licensed
copy and scope.

### 4.4 Third-party AGPL or other copyleft material

This Agreement cannot remove obligations imposed by third-party software
licenses.

If the Licensed Software includes Third-Party Materials under AGPL, GPL, LGPL,
or another copyleft license, those third-party terms continue to apply to those
materials according to their licenses.

## 5. License Metrics and Scope

The commercial scope must be defined in Schedule B using one or more metrics,
which may include:

- enterprise-wide;
- named user;
- concurrent user;
- server or virtual machine;
- Kubernetes cluster;
- physical site;
- legal entity or affiliate;
- tenant;
- robot;
- CNC machine;
- manufacturing cell;
- edge device;
- OEM unit;
- API request volume;
- CPU/GPU/QPU capacity;
- source-code seat;
- development environment;
- production environment.

Unless Schedule B states otherwise, rights are limited to Licensee and do not
automatically extend to affiliates, contractors, customers, or downstream OEM
recipients.

## 6. Restrictions

Except as expressly permitted by this Agreement, Licensee shall not:

1. distribute source code of the Licensed Software to unauthorized third
   parties;
2. sublicense, rent, lease, sell, or transfer the Licensed Software;
3. remove copyright, license, trademark, authorship, provenance, or legal
   notices;
4. misrepresent the origin or ownership of the Licensed Software;
5. use Licensor's trademarks except as expressly authorized;
6. exceed the licensed deployment metrics;
7. bypass technical entitlement controls for the purpose of exceeding licensed
   rights;
8. use Confidential Information outside the purposes of this Agreement;
9. represent experimental, simulated, or unvalidated modules as certified by
   Licensor unless Licensor has expressly provided such certification in
   writing.

Nothing in this section limits rights that cannot lawfully be restricted under
applicable law.

## 7. Modifications and Derivative Works

Unless Schedule A states otherwise, Licensee may modify the Licensed Software
solely for the Authorized Deployment.

Ownership of Licensee-authored modifications will be allocated as follows:

- Licensor retains all ownership in the pre-existing Licensed Software.
- Licensee retains ownership in independently created material to the extent it
  does not include or derive from Licensor-owned material.
- Ownership and licensing of jointly developed work, commissioned work, or
  project-specific deliverables will be specified in a statement of work or
  Schedule F.

No implied transfer of Licensor's underlying intellectual property occurs.

## 8. Source Code Access

If source-code access is included:

1. source code may be used only by authorized personnel;
2. Licensee will use reasonable security controls to prevent unauthorized
   disclosure;
3. source access does not imply a right to redistribute source code;
4. source code may contain experimental and legacy modules with differing
   maturity levels;
5. Licensee is responsible for validating modifications before production use.

## 9. Product-Family Entitlements

Licensor may provide technical entitlement records or feature flags mapping the
commercial license to product families and features.

Examples include:

- `spatial.teleoperation`
- `robotics.trajectory`
- `manufacturing.gcode`
- `research.chiral`
- `edge.device_adapters`
- `enterprise.private_api`

Technical entitlements are implementation controls only. If a technical
entitlement conflicts with this executed Agreement, the executed Agreement
controls.

## 10. Fees and Payment

Fees, currency, invoicing schedule, taxes, late-payment terms, renewal pricing,
usage charges, minimum commitments, and other commercial terms are specified in
**Schedule C (Fees and Payment)**.

Unless Schedule C states otherwise:

- fees are exclusive of applicable taxes;
- Licensee is responsible for taxes imposed on Licensee's purchase, except
  taxes based on Licensor's net income;
- payment obligations are non-cancelable after the applicable commitment date
  and fees paid are non-refundable except as expressly stated.

## 11. Records and License Verification

If the commercial model uses deployment limits, usage metrics, or per-unit
rights, Licensee will maintain reasonable records sufficient to verify
compliance.

Any audit right must be described in Schedule B or C, including:

- notice period;
- frequency;
- confidentiality;
- auditor independence;
- scope;
- cost allocation;
- remediation process.

Licensor has no unlimited inspection right merely by virtue of this template.

## 12. Support, Maintenance, and Updates

Support obligations exist only if purchased in Schedule D.

Schedule D should specify:

- support hours;
- support channels;
- severity levels;
- target response times;
- maintenance releases;
- upgrade rights;
- supported versions;
- end-of-life policy;
- professional services;
- exclusions.

Absent Schedule D, the Licensed Software is licensed without a support or
maintenance commitment.

## 13. Professional Services

Integration, implementation, customization, training, validation, hardware
adapter development, consulting, and research services may be governed by one
or more statements of work.

Each statement of work should define deliverables, acceptance criteria,
dependencies, schedule, fees, intellectual-property treatment, and change
control.

## 14. Confidentiality

Each receiving Party will:

1. use the disclosing Party's Confidential Information only for purposes of the
   Agreement;
2. protect it using at least reasonable care;
3. disclose it only to personnel and contractors who need to know and are bound
   by confidentiality obligations.

Confidential Information does not include information that the receiving Party
can demonstrate:

- was already lawfully known without confidentiality obligation;
- becomes public through no breach;
- is received lawfully from a third party without confidentiality duty;
- is independently developed without use of the Confidential Information.

Required legal disclosure is permitted after reasonable notice where lawful.

The confidentiality survival period is **[insert period]**, except trade secrets
may remain protected while legally qualifying as trade secrets.

## 15. Data Protection and Security

Each Party is responsible for its own compliance with applicable privacy,
security, cybersecurity, and data-protection law.

If Licensee supplies personal, regulated, export-controlled, health, financial,
biometric, or other sensitive data, the Parties should execute any additional
data-processing or security agreement required for that deployment.

Licensor does not assume responsibility for Licensee data merely because the
software is capable of processing it.

## 16. Hardware, Robotics, Manufacturing, and Safety-Critical Use

The Licensed Software includes modules capable of interacting with robotics,
CNC systems, sensors, RF equipment, edge devices, digital twins, and other
hardware.

Unless expressly certified in a separately signed schedule:

1. the Licensed Software is not a safety-certified control system;
2. software emergency-stop requests do not guarantee physical power removal;
3. real hardware requires independent physical interlocks and qualified
   engineering;
4. Licensee is responsible for machine guarding, workspace safety, collision
   avoidance, electrical safety, cybersecurity, operator training, and
   regulatory compliance;
5. simulation, HIL, digital-twin, or mock performance is not a certification of
   production hardware performance.

## 17. Research and Experimental Modules

Research modules may include experimental physics, numerical models, lattice
gauge systems, reciprocity geometry, chiral-fermion tooling, anomaly
diagnostics, optimization models, and other research code.

Unless expressly warranted in Schedule E:

- experimental modules are provided for research and engineering evaluation;
- mathematical consistency does not constitute experimental confirmation;
- calibrated results are not necessarily derived predictions;
- Licensee is responsible for independent validation before relying on results
  in production, regulated, or safety-critical decisions.

## 18. Third-Party Materials

Third-Party Materials are licensed under their own terms.

Licensor's commercial license does not grant rights Licensor does not own or
control.

Licensee remains responsible for complying with applicable third-party license
terms.

Where practical, Licensor will identify material third-party dependencies in
software manifests, package metadata, SBOMs, or documentation.

## 19. Intellectual Property Ownership

As between the Parties:

- Licensor owns the Licensed Software and Licensor-provided Derivative Works,
  except for Third-Party Materials and separately identified customer-owned
  material;
- Licensee owns its pre-existing technology and data;
- no intellectual-property ownership transfers except as expressly stated in a
  signed writing.

All rights not expressly granted are reserved.

## 20. Feedback

If Licensee voluntarily provides suggestions, ideas, or feedback without a
separate confidentiality or ownership restriction, Licensee grants Licensor a
worldwide, perpetual, irrevocable, royalty-free right to use and incorporate
that feedback without obligation.

This section does not transfer ownership of Licensee's code or Confidential
Information.

## 21. Trademarks

No trademark or branding license is granted except as expressly stated in
Schedule A or a separate brand agreement.

Licensee may make truthful nominative references to the Licensed Software as
permitted by law.

## 22. Warranties

Any commercial warranty must be stated in Schedule E.

Except for express warranties in Schedule E and to the maximum extent permitted
by law, the Licensed Software and services are provided "AS IS" and "AS
AVAILABLE," and Licensor disclaims implied warranties, including
merchantability, fitness for a particular purpose, title, and noninfringement.

Consumer-law rights that cannot lawfully be waived remain unaffected.

## 23. Intellectual-Property Indemnity

Any Licensor IP-indemnity obligation must be expressly stated in Schedule E,
including exclusions, defense control, notice duties, remedies, and liability
limits.

No IP indemnity is implied by this template.

## 24. Licensee Indemnity

Any Licensee indemnity for misuse, hazardous integration, regulatory violation,
customer products, or unauthorized distribution must be expressly stated in
Schedule E.

## 25. Limitation of Liability

The liability cap, excluded damages, carve-outs, and treatment of
confidentiality, security incidents, indemnity, gross negligence, willful
misconduct, and unpaid fees must be negotiated in Schedule E.

Unless a final executed Schedule E states otherwise, this template does not
establish a numerical liability cap.

## 26. Term

The Agreement begins on the Effective Date and continues for the period stated
in Schedule B unless terminated earlier under this Agreement.

License rights may be:

- subscription;
- fixed-term;
- perpetual for a specified release;
- perpetual with separately purchased maintenance;
- usage-based.

The selected structure must be stated explicitly.

## 27. Termination

Either Party may terminate for a material breach that remains uncured after
**[insert cure period]** written notice.

Immediate termination rights, if any, for insolvency, unlawful use, security
abuse, or repeated license violations should be specified in Schedule E.

On termination or expiration, Licensee will cease proprietary use beyond any
surviving rights stated in the schedules.

The Agreement should specify whether archival copies, customer deployments,
perpetual rights, data-export rights, or transition periods survive.

## 28. Effect of Termination on Public AGPL Rights

Termination of this proprietary Agreement does not itself revoke any separate
rights Licensee validly obtained under the public AGPL for publicly licensed
copies, subject to the AGPL's own terms and termination provisions.

## 29. Export, Sanctions, and Trade Compliance

Each Party will comply with applicable export-control, sanctions, customs, and
trade laws.

Licensee is responsible for determining whether its intended hardware,
cryptography, RF, aerospace, defense, semiconductor, AI, or cross-border use
requires additional authorization.

## 30. Compliance with Laws

Each Party will comply with laws applicable to its own performance under the
Agreement.

A software license does not transfer Licensee's regulatory obligations to
Licensor.

## 31. Publicity

Neither Party may issue a press release or use the other Party's name, logo, or
trademarks in marketing without prior written approval, except for truthful
statements required by law or expressly permitted in a schedule.

## 32. Assignment

Neither Party may assign this Agreement except as specified in Schedule E or
with the other Party's written consent, provided that an agreed exception may
permit assignment in connection with merger, reorganization, or sale of
substantially all relevant assets.

## 33. Independent Contractors

The Parties are independent contractors. The Agreement does not create a
partnership, joint venture, fiduciary relationship, franchise, employment
relationship, or agency.

## 34. Force Majeure

Any force-majeure provision, including excluded payment obligations and notice
requirements, should be specified in Schedule E.

## 35. Notices

Formal notices must be delivered to the addresses stated in Schedule G using
the permitted methods specified there.

Commercial licensing inquiries may be sent to:
waterslegacytrust@gmail.com

## 36. Governing Law and Dispute Resolution

The Parties must complete **Schedule G (Legal Terms)** to specify:

- governing law;
- exclusive or nonexclusive forum;
- arbitration, if any;
- venue;
- jury-waiver terms, if any;
- prevailing-party attorneys' fees, if any.

No governing jurisdiction is implied by this template.

## 37. Entire Agreement and Order of Precedence

The executed Agreement, including its schedules and signed statements of work,
constitutes the entire agreement concerning its subject matter and supersedes
prior proposals concerning the proprietary commercial license.

Unless otherwise stated, the order of precedence is:

1. signed amendment;
2. applicable signed statement of work;
3. Schedule E for negotiated risk terms;
4. other schedules;
5. main Agreement.

The public AGPL remains a separate license path rather than a subordinate
schedule to this Agreement.

## 38. Amendment and Waiver

Amendments must be in a writing signed by authorized representatives of both
Parties.

A waiver in one instance does not waive future enforcement.

## 39. Severability

If a provision is held unenforceable, the remaining provisions remain effective
to the maximum extent permitted by law, and the Parties will seek a valid term
that most closely reflects the original commercial intent.

## 40. Counterparts and Electronic Signatures

The Agreement may be executed in counterparts and by electronic signature, each
of which is deemed an original and together form one instrument.

---

# Schedule A: Licensed Scope

**Product family or families:** [insert]

**Repository paths/modules:** [insert]

**Version/tag/commit:** [insert]

**Source-code access:** [yes/no and scope]

**Modification rights:** [insert]

**Distribution/OEM rights:** [insert]

**Permitted affiliates/contractors:** [insert]

**Excluded modules:** [insert]

**Trademark/branding rights, if any:** [insert]

---

# Schedule B: Deployment, Metrics, and Term

**License model:** [subscription / perpetual / usage / OEM / enterprise]

**Term:** [insert]

**Sites:** [insert]

**Devices/robots/machines:** [insert]

**Servers/clusters:** [insert]

**Tenants/users:** [insert]

**OEM units:** [insert]

**Production environments:** [insert]

**Development/test environments:** [insert]

**Geographic scope:** [insert]

**Affiliate rights:** [insert]

**Contractor rights:** [insert]

**Verification/audit process:** [insert]

---

# Schedule C: Fees and Payment

**License fee:** [insert]

**Usage fees:** [insert]

**Support fees:** [insert]

**Professional-services rates:** [insert]

**Currency:** [insert]

**Invoice schedule:** [insert]

**Payment terms:** [insert]

**Taxes:** [insert]

**Renewal pricing:** [insert]

---

# Schedule D: Support and Maintenance

**Support plan:** [insert]

**Supported versions:** [insert]

**Support hours/time zone:** [insert]

**Channels:** [insert]

**Severity definitions:** [insert]

**Response targets:** [insert]

**Maintenance releases:** [insert]

**Upgrade rights:** [insert]

**End-of-life terms:** [insert]

---

# Schedule E: Warranty, Liability, Indemnity, and Risk Allocation

**Express warranty:** [insert]

**Warranty period:** [insert]

**Liability cap:** [insert]

**Excluded damages:** [insert]

**Carve-outs:** [insert]

**Licensor indemnity:** [insert]

**Licensee indemnity:** [insert]

**Insurance requirements:** [insert]

**Safety-critical restrictions/certifications:** [insert]

**Security obligations:** [insert]

---

# Schedule F: Professional Services and Development

**Statement(s) of work:** [attach/insert]

**Deliverables:** [insert]

**Acceptance criteria:** [insert]

**Milestones:** [insert]

**Customer dependencies:** [insert]

**Custom IP ownership:** [insert]

**Background IP:** [insert]

**Maintenance of custom work:** [insert]

---

# Schedule G: Legal Terms and Notices

**Licensor legal name/address:** [insert]

**Licensee legal name/address:** [insert]

**Notice email/address:** [insert]

**Governing law:** [insert]

**Forum/venue:** [insert]

**Arbitration:** [insert]

**Attorneys' fees:** [insert]

**Confidentiality survival:** [insert]

**Assignment exceptions:** [insert]

**Force majeure:** [insert]

---

# Signatures

**WATERS LEGACY TRUST**

By: __________________________________

Name: ________________________________

Title/Capacity: _______________________

Date: _________________________________


**LICENSEE: [LEGAL NAME]**

By: __________________________________

Name: ________________________________

Title: _______________________________

Date: _________________________________
