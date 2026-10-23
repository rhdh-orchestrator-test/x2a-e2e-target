# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository presents a **unique migration scenario**: it is not a traditional Chef cookbook repository requiring migration, but rather an **example/demonstration repository** that already contains Ansible playbooks alongside Chef InSpec compliance tests. The repository demonstrates the integration pattern between Ansible for configuration management and Chef InSpec for compliance verification.

**Key Finding**: The core configuration management code is **already implemented in Ansible**. The Chef components present are:
- Chef InSpec profiles used for compliance testing and verification (not configuration management)
- Infrastructure deployment scripts for Chef Server and Chef Automate (infrastructure setup, not application configuration)

**Migration Scope**: Minimal. This is primarily a **documentation and testing framework migration** rather than a code migration.

**Complexity**: Low  
**Estimated Timeline**: 1-2 weeks (primarily for InSpec test conversion and validation)

---

## Module Migration Plan

This repository does not contain traditional Chef cookbooks that need migration. Instead, it contains:

### ANSIBLE PLAYBOOKS (Already Migrated)
These playbooks are already in Ansible format and require no migration:

- **website_https**:
    - Description: Apache web server configuration with HTTPS/SSL support using self-signed certificates, including virtual host setup for a "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (native)
    - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation (self-signed), virtual host configuration, DocumentRoot at /var/www/helloworld, SSL/TLS configuration with TLSv1.2

- **poodle_fix**:
    - Description: Security remediation playbook to address POODLE vulnerability by enforcing TLS 1.2 and disabling older SSL protocols in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (native)
    - Key Features: Apache SSL protocol hardening, TLS 1.2 enforcement, service restart handlers for apache2 and sshd

### CHEF INSPEC COMPLIANCE TESTS
These are compliance verification tests, not configuration management code:

- **website_https_verify**:
    - Description: InSpec profile verifying HTTPS website functionality, SSL/TLS protocol configuration, and security posture
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port 443 listener verification, HTTPS response validation (200 status, body content), SSL3 protocol disabled check, TLS 1.2 enabled verification

- **ssh_profile**:
    - Description: InSpec security compliance profile enforcing SSH root login restrictions per STIG requirements (RHEL-08-000227, V-38607)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: PermitRootLogin configuration check, STIG/CCI compliance tagging (CCI-000774, SRG-OS-000112), CAT I severity control

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing using vagrant driver, ansible_playbook provisioner, and InSpec verifier targeting Ubuntu 20.04
- `chef-and-ansible/index.html`: Static HTML test file for website verification (Hello World content)
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server infrastructure (creates users, organizations, configures hostnames)
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only without Automate (similar setup to deploy-automate.sh but limited scope)
- `README.md`: Repository documentation describing Chef examples for Technical Product Marketing and Developer Relations content
- `chef-and-ansible/README.md`: Documentation explaining the use of Chef InSpec with Ansible for compliance automation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml platforms configuration)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver configuration)
- **Cloud Platform**: Not specified (designed for on-premises or cloud VM deployment per deployment scripts)

---

## Migration Approach

### Key Dependencies to Address

**No Chef Configuration Management Dependencies Exist** - The Ansible playbooks use native Ansible modules only:

- **Apache 2.4.41**: Already managed via Ansible `apt` module - no migration needed
- **OpenSSL Python libraries (python3-openssl)**: Already managed via Ansible `apt` module for certificate generation - no migration needed
- **Test Kitchen**: Used for testing infrastructure - can be retained or replaced with Molecule for pure Ansible testing workflows
- **Chef InSpec**: Currently used for compliance verification - consider migrating to **Ansible compliance modules** or **OpenSCAP** for native Ansible compliance testing

### Security Considerations

**Certificate and Key Management**:
- Self-signed certificates generated via Ansible `openssl_*` modules at `/etc/apache2/certs/`
- Private keys stored with 0640 permissions
- No external vault or secrets management detected
- **Migration Strategy**: Already using Ansible native approach; consider implementing Ansible Vault for any sensitive variables (currently hardcoded in playbook vars)

**SSL/TLS Configuration**:
- TLS 1.2 enforcement already implemented in Ansible playbooks
- POODLE vulnerability mitigation already in place
- **Migration Strategy**: No changes needed; security best practices already followed

**SSH Hardening**:
- InSpec profile verifies PermitRootLogin restrictions
- STIG compliance controls embedded in tests
- **Migration Strategy**: Implement Ansible tasks to enforce SSH hardening if not already deployed; currently only verified, not enforced by configuration management

**Credentials in Deployment Scripts**:
- Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password, email)
- **Migration Strategy**: Extract credentials to environment variables or Ansible Vault; never commit credentials to version control

### Technical Challenges

**Challenge 1: InSpec Test Migration**
- **Description**: Chef InSpec provides rich compliance testing capabilities not natively available in Ansible. The repository uses InSpec for SSL/TLS protocol verification and SSH configuration validation.
- **Mitigation Strategy**: 
  - Option A: Continue using InSpec alongside Ansible (recommended for compliance-heavy environments)
  - Option B: Migrate to Ansible's built-in assertion modules (`uri`, `assert`, `service_facts`) for basic checks
  - Option C: Adopt OpenSCAP profiles for STIG compliance validation
  - Option D: Use Ansible Molecule with InSpec verifier (maintain current testing approach)

**Challenge 2: Test Kitchen Integration**
- **Description**: Current testing workflow uses Test Kitchen with Vagrant driver and InSpec verifier, which is a Chef ecosystem tool.
- **Mitigation Strategy**: 
  - Option A: Replace with Molecule (Ansible's native testing framework) while retaining InSpec as verifier
  - Option B: Keep Test Kitchen if team is familiar with the workflow (it supports Ansible provisioner)
  - Recommended: Migrate to Molecule for consistency with Ansible ecosystem

**Challenge 3: Chef Infrastructure Dependencies**
- **Description**: The `setup-automate/` scripts deploy Chef Server and Automate infrastructure, which may be needed for InSpec testing or other organizational Chef usage.
- **Mitigation Strategy**: 
  - Assess if Chef Server/Automate is still required for other organizational needs
  - If only needed for InSpec, InSpec can run standalone without Chef Server
  - If Chef infrastructure is being decommissioned, coordinate timing with this migration
  - Consider migrating deployment scripts to Ansible playbooks for consistency

**Challenge 4: Compliance Framework Alignment**
- **Description**: InSpec tests include STIG IDs, CCI codes, and vulnid references for compliance tracking. Migrating away from InSpec requires maintaining this compliance metadata.
- **Mitigation Strategy**: 
  - If migrating tests to native Ansible, preserve compliance metadata in task tags and comments
  - Consider using Ansible's STIG-compliant roles from the Ansible security automation content
  - Document mapping between InSpec controls and replacement Ansible assertions

### Migration Order

Given that the core configuration management is already in Ansible, the "migration" is primarily about standardizing the testing and deployment infrastructure:

1. **Phase 1: Documentation and Inventory (Week 1)**
   - Document current testing workflow and dependencies
   - Identify all consumers of InSpec test results
   - Catalog any external dependencies on Chef infrastructure
   - Assess team InSpec vs. Ansible testing skills

2. **Phase 2: Testing Framework Migration (Week 1-2)**
   - Option A: Migrate to Molecule with InSpec verifier (maintains InSpec tests, changes runner)
   - Option B: Convert InSpec tests to Ansible assertions (if pure Ansible stack is required)
   - Validate test coverage matches original InSpec profiles
   - Update CI/CD pipelines to use new testing framework

3. **Phase 3: Infrastructure Script Migration (Week 2 - Optional)**
   - Convert Chef Server/Automate deployment scripts to Ansible playbooks if infrastructure is retained
   - Or decommission scripts if Chef infrastructure is no longer needed
   - Document infrastructure dependencies and transition plan

4. **Phase 4: Cleanup and Documentation (Week 2)**
   - Remove or archive Chef-specific tooling if no longer needed
   - Update README files to reflect pure Ansible approach
   - Document new testing and deployment workflows
   - Conduct team knowledge transfer sessions

### Assumptions

1. **Primary Assumption**: This repository is intended as an **example/demonstration** of Ansible + InSpec integration, not a production configuration management codebase. If this is production code, the migration scope is even smaller as the configuration management is already in Ansible.

2. **Chef Server Dependency**: It is unclear whether the organization still requires Chef Server/Automate infrastructure for other purposes beyond this repository. The deployment scripts suggest infrastructure may still be in use elsewhere.

3. **InSpec Test Consumers**: Unknown if InSpec test results are consumed by compliance reporting systems, dashboards, or external tools that expect InSpec JSON output format. This would impact migration decisions.

4. **Testing Framework Preference**: No stated preference for pure Ansible testing vs. polyglot approach (Ansible + InSpec). Many organizations successfully use InSpec with Ansible for compliance testing.

5. **STIG Compliance Requirements**: The presence of STIG control IDs suggests a compliance-regulated environment. The migration approach assumes these compliance requirements must be maintained with full traceability.

6. **Team Skills**: Assumes team has Ansible skills (evidenced by existing playbooks) but may have varying InSpec expertise. Training needs for pure Ansible testing frameworks may exist.

7. **CI/CD Integration**: Assumes existing CI/CD pipelines integrate with Test Kitchen and InSpec. Migration would require pipeline updates, but current pipeline configuration is not visible in this repository.

8. **Version Pinning**: The playbook pins Apache to version 2.4.41-4ubuntu3.10, suggesting this is production-tested configuration. Migration must preserve this version control approach.

9. **Ubuntu Target OS**: All examples target Ubuntu 20.04. No indication of multi-OS support needs or RHEL targets (despite RHEL STIG references in InSpec tests).

10. **No External Dependencies**: The Ansible playbooks have no external role dependencies (no `requirements.yml`, no Galaxy roles). All functionality uses built-in Ansible modules, simplifying maintenance.

11. **Self-Signed Certificates**: Production use of self-signed certificates suggests this is a development/testing environment, or certificates are replaced post-deployment. Production migration may need Let's Encrypt or enterprise PKI integration.

12. **Secrets Management Gap**: Neither the Ansible playbooks nor deployment scripts use a secrets management solution (no Ansible Vault, no Hashicorp Vault references). Production hardening would require addressing this regardless of migration approach.

---

## Conclusion

This repository requires **minimal migration effort** because the configuration management code is already written in Ansible. The effort should focus on:

1. **Standardizing the testing framework** (Test Kitchen + InSpec vs. Molecule, or maintaining current approach)
2. **Addressing security gaps** (secrets management, credential handling in deployment scripts)
3. **Documenting the intended integration pattern** for teams adopting this approach

**Recommendation**: Rather than "migration," treat this as a **testing framework modernization** and **security hardening** initiative. The core Ansible playbooks are production-ready and follow best practices. Focus optimization efforts on the testing and deployment infrastructure surrounding them.
