# Universal Matrix Licensing Guide

This guide explains the repository's licensing structure in plain English.

It is not legal advice and does not replace the actual AGPL text or an executed
commercial license agreement.

## 1. Public license

Universal Matrix is publicly offered under:

**GNU Affero General Public License v3.0 or later**
**SPDX:** `AGPL-3.0-or-later`

The AGPL permits both commercial and noncommercial use.

It is a strong copyleft license. Its obligations can include source-code,
license-notice, same-license, and network-source obligations depending on how
the covered software is modified, conveyed, combined, or made available over a
network.

The authoritative AGPL text is published by the Free Software Foundation.

## 2. Why a commercial license exists

The proprietary commercial license is not required merely because a user makes
money.

It is an alternative license path for customers who want rights or obligations
different from the public AGPL option.

Common examples include:

- closed-source SaaS;
- proprietary OEM products;
- closed-source robotics deployments;
- proprietary XR or digital-twin products;
- private manufacturing systems;
- redistribution rights;
- customer-specific proprietary derivatives;
- negotiated warranties, indemnities, support, SLAs, or confidentiality;
- enterprise source access under private terms.

## 3. What the commercial license can cover

Commercial licenses may cover all or part of the platform.

Product families currently include:

- Universal Matrix Core
- Universal Matrix Spatial
- Universal Matrix Robotics
- Universal Matrix Manufacturing
- Universal Matrix Research
- Universal Matrix Edge
- Universal Matrix Enterprise

The executed agreement should identify exactly which product families, modules,
versions, sites, devices, tenants, users, or OEM units are licensed.

## 4. Public AGPL and commercial rights are alternatives

A customer can use a publicly licensed copy under the AGPL if the customer
complies with the AGPL.

A customer with a proprietary Waters Legacy Trust commercial license can use
the licensed commercial copy under the negotiated agreement instead.

The commercial agreement does not take away AGPL rights already validly granted
to recipients of public copies.

## 5. Third-party dependencies

Waters Legacy Trust can license only rights it owns or controls.

Third-party libraries, models, assets, datasets, standards material, and other
dependencies remain subject to their own licenses.

A Waters Legacy Trust commercial license does not erase third-party
obligations.

## 6. Contributor licensing

External contributors retain ownership of their contributions.

Under `CLA.md`, contributors grant Waters Legacy Trust broad copyright and
patent rights needed to:

- include the contribution in the project;
- distribute it under AGPL;
- sublicense it;
- include it in proprietary commercial licenses;
- relicense the project in the future.

This is what makes dual licensing sustainable after outside contributions are
accepted.

## 7. Product entitlements are not the legal license

`src/commercial_entitlements.py` models commercial product families and
features in software.

Those feature flags are technical controls only.

If software configuration conflicts with an executed agreement, the executed
agreement controls.

## 8. Commercial agreement documents

The repository contains:

- `LICENSE` — public AGPL notice and dual-license clarification;
- `NOTICE` — project copyright and licensing notice;
- `COMMERCIAL_LICENSE.md` — commercial licensing overview;
- `COMMERCIAL_LICENSE_AGREEMENT_TEMPLATE.md` — full negotiated agreement
  template;
- `CLA.md` — contributor license agreement;
- `CONTRIBUTING.md` — contribution and governance rules.

## 9. Commercial agreement structure

The commercial agreement template includes:

- licensed scope;
- product families;
- deployment metrics;
- proprietary grant;
- source-code rights;
- OEM and redistribution rights;
- modifications and derivative works;
- product entitlements;
- fees;
- support;
- professional services;
- confidentiality;
- security and data protection;
- hardware and safety-critical use;
- research/experimental module limitations;
- third-party materials;
- IP ownership;
- trademarks;
- warranties;
- indemnity;
- liability;
- term and termination;
- export and sanctions;
- assignment;
- force majeure;
- governing law and dispute resolution;
- signature blocks.

Deal-specific legal and financial terms remain schedules to be negotiated.

## 10. What must be completed before signing

Before a commercial agreement is executed, the parties should complete at
least:

1. Licensor legal name, address, and capacity.
2. Licensee legal name and address.
3. Effective date.
4. Licensed product families and repository scope.
5. Release, commit, or artifact version.
6. Deployment model and metrics.
7. Fees and payment.
8. Term and renewal.
9. Support obligations.
10. Warranty terms.
11. Liability cap.
12. Indemnity terms.
13. Confidentiality duration.
14. Security/data requirements.
15. Governing law.
16. Venue or arbitration.
17. Notice addresses.
18. Authorized signatories.

## 11. Safety and regulated deployments

A software license is not a safety certification.

Robotics, manufacturing, RF, medical, automotive, aerospace, energy, and other
regulated uses require separate engineering, validation, certification, and
compliance work.

## 12. Commercial contact

Waters Legacy Trust

waterslegacytrust@gmail.com
