# ADR 0001: Installation and Environment Management

**Status**: Accepted

---

## Problem Statement

Architekta requires an appropriate installation strategy to ensure usability across multiple
projects while maintaining environment isolation.

The toolkit interacts with Conda environments and needs to be available early in the project setup
workflows.

**Questions to be addressed**:
1. How should users install and use Architekta to initialize their projects while ensuring it
   remains available within their project-specific Conda environments?
2. How to prevent redundancy in installation while keeping the tool accessible when needed?

---

## Decision Drivers

- **Modularity**: Allow independent management of project environments.
- **Usability**: Minimize friction for users starting new projects (i.e. effort required to set up a
  new project).
- **Maintainability**: Facilitate version management and prevent conflicts between projects.
- **Portability**: Work across different operating systems and user setups (i.e. using other package
  managers or virtual environments than conda).

---

## Considered Options

### Hybrid Approach: Global CLI with Project Integration

1. Install Architekta in a *dedicated persistent environment* (`architekta-env`).
   ```sh
   conda create -n architekta-env python pip
   conda activate architekta-env
   pip install architekta
   ```
2. Run Architekta to initialize the project (*before* setting up a project-specific Conda
   environment):
   ```sh
   architekta init my_project
   cd my_project
   ```
3. Architekta generates a structured `environment.yml` that *includes itself as a dependency*.
4. Users create the project environment from `environment.yml`, ensuring Architekta is available
   inside it:
   ```sh
   conda env create -f environment.yml
   conda activate my_project
   ```

### Installing Architekta in Each Project's Conda Environment

- They run Architekta
-  and use to update the
  Conda environment.

**Workflow:**
1. Users manually create a minimal Conda environment:
   ```sh
   conda create -n my_project python
   conda activate my_project
   ```
2. Install Architekta inside this environment:
   ```sh
   pip install architekta
   ```
3. Run Architekta inside the project's environment to initialize the project:
   ```sh
   architekta init
   ```
4. Architekta generates a structured `environment.yml` that includes itself, which users can edit to
   add other dependencies.
5. Edit and update the generated `environment.yml`:
   ```sh
   conda env update --file environment.yml --prune
   ```

---

## Analysis of Options

### **Hybrid Approach: Global CLI with Project Integration**

**Pros:**
- Ensures Architekta is always available when needed.
- Avoids redundant manual installations per project.
- Allows pre-setup before the project environment exists.
- Keeps project environments isolated and independent.

**Cons:**
- Requires an initial installation in a global persistent environment.
- Users need to manage updates separately for the global and project environments.

### **Installing Architekta in Each Project's Conda Environment**

**Pros:**
- Keeps each project environment self-contained, avoiding dependencies outside the project.
- Allows each project to use different versions of Architekta as needed.
- Ensures that the correct version of Architekta is always available inside the project
  environment.

**Cons:**
- Users must manually create and set up the Conda environment before running Architekta.
- Redundant installation in every project, leading to unnecessary duplication.
- Architekta is unavailable before the project environment exists, requiring a manual install
  step.

## Summary: Comparison by Criteria

- **Modularity**:
  - **Hybrid Approach**: High (separates tool environment from project environments)
  - **Per-Project Installation**: Medium (isolated but requires duplicate installations)

- **Usability**:
  - **Hybrid Approach**: High (simplifies initial setup)
  - **Per-Project Installation**: Low (requires manual environment creation)

- **Maintainability**:
  - **Hybrid Approach**: High (avoids redundant installs, centralizes updates)
  - **Per-Project Installation**: Medium (version isolation per project but higher maintenance
    overhead)

- **Portability**:
  - **Hybrid Approach**: High (works in different environments without modifications)
  - **Per-Project Installation**: High (self-contained but requires setup per project)

---

## Conclusions

### Decision

**Chosen option**: Hybrid Approach: Global CLI with Project Integration

**Justification**: This approach provides the best balance between modularity, usability, and
maintainability. It ensures that Architekta is always accessible while keeping individual project
environments isolated and self-contained. It also extends better to use pip instead of conda.

### Final Answers

1. **How should users install and use Architekta?**
   - They should install Architekta in a persistent `architekta-env` (if using conda) and use it to
     initialize project environments where it will be included automatically.

2. **How to prevent redundancy in installation while keeping the tool accessible?**
   - By using a global CLI for initial setup and ensuring it is included in the project-specific
     `environment.yml`, redundancy is minimized while maintaining accessibility.

---

## Implications

- Provide clear documentation on this installation process.
- Handle automatic inclusion of Architekta in `environment.yml`.
- Future enhancements could include a mechanism for automatic version selectin between global and
  project installations.
