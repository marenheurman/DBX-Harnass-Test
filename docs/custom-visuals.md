# Custom Visuals

## Overview

Custom visuals extend the Power BI report canvas beyond the built-in visual library. They are developed using the **Power BI Visuals SDK** and distributed as `.pbiviz` packages. This document covers the types of custom visuals available in Power BI, how to evaluate and govern their use, and how to build your own using the official SDK toolchain.

> **Important:** Custom visuals execute JavaScript code inside the report rendering environment. Always apply appropriate governance controls before deploying custom visuals — particularly in workspaces containing sensitive or regulated data.

---

## Visual Sources and Classification

| Type | Source | Certification | Risk Level | Usage Guideline |
|------|--------|---------------|------------|-----------------|
| Microsoft built-in | Power BI Desktop | N/A — first party | Low | Always preferred |
| AppSource Certified | Published + Microsoft-reviewed | Microsoft Certified | Medium | Approved for use in DEV, UAT, PROD |
| AppSource Uncertified | Published, no Microsoft review | None | High | DEV/UAT only without security review |
| Organisational | Uploaded via Power BI Admin | Admin-approved | Medium | Approved once admin has reviewed |
| In-house built | Internal team development | None (internal) | High | Requires code review + security sign-off before PROD |

**Certified** AppSource visuals have passed Microsoft's security and quality review. They also support the Power BI "export to PDF/PowerPoint" feature. Uncertified visuals may not support these features and have not been independently reviewed.

---

## Governance Requirements by Environment

| Environment | Permitted Visual Sources |
|-------------|--------------------------|
| Development (DEV) | All types permitted for exploration |
| User Acceptance Testing (UAT) | Certified AppSource, Organisational visuals. Uncertified visuals only with documented approval |
| Production (PROD) | Certified AppSource and Organisational visuals only. In-house visuals require sign-off |

Power BI admins can enforce "allow only certified visuals" at the tenant level. Whether this restriction is active in your environment should be confirmed as part of the project governance plan.

---

## Building Custom Visuals

### Prerequisites

You need Node.js (LTS), npm, and the Power BI Visuals Tools CLI:

```powershell
# Install the Power BI Visuals Tools globally
npm install -g powerbi-visuals-tools

# Verify the installation
pbiviz --version
```

Also install the Power BI certificate for local development mode:

```powershell
pbiviz --install-cert
```

---

### Scaffolding a New Visual

```powershell
# Create a new visual project
pbiviz new MyCustomVisual

# Navigate into the project folder
Set-Location MyCustomVisual
```

This generates the full project structure.

---

### Project Structure

```
MyCustomVisual/
│
├── .api/                        ← SDK type definitions (auto-generated, do not edit)
│
├── assets/
│   └── icon.png                 ← Visual icon shown in the visual picker
│
├── src/
│   ├── visual.ts                ← Main visual class — your rendering logic lives here
│   └── settings.ts              ← Format pane property definitions
│
├── style/
│   └── visual.less              ← Visual styling (LESS/CSS)
│
├── test/
│   └── visualTest.ts            ← Unit test files
│
├── pbiviz.json                  ← Visual manifest (name, GUID, version, author)
├── capabilities.json            ← Data roles, data view mappings, format pane objects
├── tsconfig.json                ← TypeScript configuration
└── package.json                 ← Node.js dependencies
```

---

### Key Configuration Files

#### `pbiviz.json` — Visual Manifest

```json
{
  "visual": {
    "name": "MyCustomVisual",
    "displayName": "My Custom Visual",
    "guid": "MyCustomVisual_XXXXXXXXXXXXXXXX",
    "visualClassName": "Visual",
    "version": "1.0.0",
    "description": "A description of what this visual does",
    "supportUrl": "",
    "gitHubUrl": ""
  },
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "apiVersion": "5.3.0",
  "style": "style/visual.less",
  "capabilities": "capabilities.json"
}
```

#### `capabilities.json` — Data Roles and Mappings

This file defines what the visual accepts from the field well and how data is exposed to the visual code.

```json
{
  "dataRoles": [
    {
      "displayName": "Category",
      "name": "category",
      "kind": "Grouping"
    },
    {
      "displayName": "Values",
      "name": "measure",
      "kind": "Measure"
    }
  ],
  "dataViewMappings": [
    {
      "categorical": {
        "categories": {
          "for": { "in": "category" }
        },
        "values": {
          "select": [{ "bind": { "to": "measure" } }]
        }
      }
    }
  ],
  "objects": {
    "colorSelector": {
      "displayName": "Data Colors",
      "properties": {
        "fill": {
          "displayName": "Color",
          "type": { "fill": { "solid": { "color": true } } }
        }
      }
    }
  }
}
```

**`kind` values for `dataRoles`:**
- `Grouping` — categorical fields (dimensions)
- `Measure` — numeric aggregations
- `GroupingOrMeasure` — accepts either

---

### Development Workflow

#### Step 1: Start the Development Server

```powershell
pbiviz start
```

This launches a local HTTPS dev server. The visual is served live and hot-reloads as you save changes.

#### Step 2: Enable Developer Mode in Power BI Desktop

1. Open Power BI Desktop
2. Go to **File → Options and settings → Options → Security**
3. Enable **"Enable custom visual developer mode"**

A developer visual tile will appear in the Visuals pane. Clicking it loads your live local visual.

#### Step 3: Implement the Visual

The main entry point is `src/visual.ts`. The class must implement the `IVisual` interface:

```typescript
import powerbi from "powerbi-visuals-api";
import IVisual = powerbi.extensibility.visual.IVisual;
import VisualConstructorOptions = powerbi.extensibility.visual.VisualConstructorOptions;
import VisualUpdateOptions = powerbi.extensibility.visual.VisualUpdateOptions;

export class Visual implements IVisual {
    private target: HTMLElement;

    constructor(options: VisualConstructorOptions) {
        this.target = options.element;
    }

    public update(options: VisualUpdateOptions) {
        // options.dataViews contains the data mapped from capabilities.json
        // options.viewport contains the visual dimensions
        // Render your visual here
    }
}
```

The `update` method is called every time:
- The visual is resized
- A slicer selection changes
- The report page loads or refreshes

#### Step 4: Package the Visual

```powershell
pbiviz package
```

This produces a `.pbiviz` file in the `dist/` folder, which can be imported into Power BI Desktop or uploaded to the organisational visual store.

---

### Testing

Run unit tests with:

```powershell
npm run test
```

Tests live in the `test/` folder and use the `powerbi-visuals-utils-testutils` package for mocking the Power BI API surface. Write tests that cover:
- Rendering with valid data
- Rendering with empty/null data
- Format pane property changes
- Viewport resizing behaviour

---

### AppSource Submission and Certification

To submit to AppSource:
1. Create a Microsoft Partner Center account
2. Package the visual: `pbiviz package`
3. Submit via the [Partner Center Marketplace Offers portal](https://partner.microsoft.com/dashboard)
4. For **Microsoft Certification**, the visual must:
   - Pass automated security scanning
   - Not make external network calls
   - Not use `eval()` or dynamic code execution
   - Handle empty data states gracefully
   - Support high contrast mode

---

## What Agents Can and Cannot Inspect

Agents interacting via the Power BI Model MCP server or PBIP files have limited visibility into custom visuals:

| What Agents Can Do | What Agents Cannot Do |
|--------------------|-----------------------|
| Read the report JSON to identify which custom visuals are present and their GUID/version | Render or execute the visual |
| Check whether a custom visual's data roles are populated with the correct field types | Inspect the compiled JavaScript inside a `.pbiviz` file |
| Flag the visual's certification status based on GUID lookup | Validate the visual's internal logic or security posture |
| Flag visuals not on the approved list as per governance tier | Test visual behaviour under filter context changes |

When an agent encounters a custom visual during a report review, it should:
1. Note the visual name and GUID
2. State whether it is AppSource Certified, Organisational, or Unknown
3. Flag it as requiring human verification if it is uncertified or unrecognised
4. Check that the data roles are connected (not empty)

---

## Security Considerations

- Custom visuals run as sandboxed JavaScript within an iframe, but uncertified visuals are not independently reviewed
- Visuals can read all data passed to them via data roles — ensure RLS is correctly restricting the data before it reaches the visual
- Avoid uncertified visuals on reports containing personally identifiable information, financial data, or data subject to regulatory compliance (GDPR, HIPAA, etc.)
- For in-house visuals, conduct a code review focused on: absence of `eval()`, no `XMLHttpRequest` or `fetch` to external URLs, no data written to `localStorage` or `sessionStorage`
- Check with your Power BI tenant admin whether "certified visuals only" is enforced — if not, consider recommending this as a tenant policy for PROD workspaces

---

## References

- Microsoft Learn: [Power BI Visuals SDK overview](https://learn.microsoft.com/power-bi/developer/visuals/power-bi-custom-visuals)
- Microsoft Learn: [Develop a Power BI circle card visual](https://learn.microsoft.com/power-bi/developer/visuals/develop-circle-card)
- Microsoft Learn: [AppSource certification requirements for custom visuals](https://learn.microsoft.com/power-bi/developer/visuals/power-bi-custom-visuals-certified)
- Microsoft Learn: [Organisational visuals in Power BI](https://learn.microsoft.com/power-bi/developer/visuals/power-bi-custom-visuals-organization)
- [Power BI Visuals Tools (pbiviz) on npm](https://www.npmjs.com/package/powerbi-visuals-tools)
- [rules/report-rules.md](../rules/report-rules.md)
- [docs/governance.md](governance.md)
