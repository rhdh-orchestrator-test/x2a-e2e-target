# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

## Executive Summary

This repository represents a **unique migration scenario**: it is already primarily Ansible-based, with Chef InSpec used exclusively for compliance testing and verification. The repository contains demonstration content showing how Chef InSpec integrates with Ansible playbooks for continuous compliance automation.

**Migration Scope**: Low complexity - This is not a traditional Chef cookbook migration. The infrastructure automation is already written in Ansible. The migration primarily involves replacing Chef InSpec compliance tests with Ansible-native solutions.

**Estimated Timeline**: 1-2 weeks
- 2-3 days: Replace Chef InSpec tests with Ansible compliance modules
- 1-2 days: Convert Test Kitchen to Molecule for integration testing
- 2-3 days: Update deployment scripts and documentation
- 2-3 days: Testing, validation, and knowledge transfer

**Key Finding**: The Ansible playbooks (`website_https.yml`, `poodle_fix.yml`) are production-ready and require no migration. Only the testing and verification layer needs conversion.

## Module Migration Plan

This repository does not contain traditional Chef cookbooks. Instead, it contains:
- **Ansible playbooks** (already in target format)
- **Chef InSpec compliance tests** (requires migration to Ansible alternatives)
- **Test Kitchen configuration** (requires migration to Molecule)
- **Chef Automate/Server deployment scripts** (informational only)

### MODULE INVENTORY

This repository contains no Chef cookbooks or recipes to migrate. All infrastructure automation is already implemented in Ansible playbooks:

**EXISTING ANSIBLE PLAYBOOKS (No Migration Required):**

- **website_https playbook**:
    - Description: Apache2 web server configuration with HTTPS/SSL setup using self-signed certificates, virtual host configuration for a "Hello World" test site, and SSL/TLS enablement
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache 2.4.41 installation on Ubuntu 20.04, OpenSSL certificate generation (private key, CSR, self-signed cert), virtual host configuration for HTTPS on port 443, website content deployment, service management with handlers

- **poodle_fix playbook**:
    - Description: SSL/TLS protocol hardening for Apache web server to mitigate POODLE vulnerability by enforcing TLS 1.2 only
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration modification to disable SSLv3 and enforce TLSv1.2, service restart handlers for apache2 and sshd

**COMPLIANCE TESTING (Requires Migration):**

- **website_https_verify InSpec profile**:
    - Description: Chef InSpec compliance tests verifying HTTPS service availability, SSL/TLS protocol configuration, and website content
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port 443 listening verification, HTTP 200 status check with body content validation, SSL protocol verification (SSLv3 disabled, TLS 1.2 enabled)
    - **Migration Target**: Ansible assert tasks, ansible.builtin.uri module, or community.crypto validation

- **ssh_profile InSpec profile**:
    - Description: SSH security compliance test ensuring root login via SSH is disabled per STIG requirements (RHEL-08-000227, SRG-OS-000112)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: STIG-based compliance control (V-38607, CAT I severity), sshd_config PermitRootLogin validation, openssh-server package check
    - **Migration Target**: Ansible assert module with ansible.builtin.lineinfile check or custom compliance role

### Infrastructure Files

- **kitchen.yml**: Test Kitchen configuration for integration testing using Vagrant driver, Ansible provisioner, and InSpec verifier on Ubuntu 20.04 platform
  - Migration: Replace with Molecule (molecule.yml) using similar driver/provisioner pattern
  
- **setup-automate/deploy-automate.sh**: Bash script for deploying Chef Automate and Chef Infra Server with user and organization setup
  - Migration: Informational only - not required for Ansible-only environment unless Chef Automate is being retained for compliance reporting
  
- **setup-automate/deploy-chef-server.sh**: Bash script for deploying standalone Chef Infra Server without Automate
  - Migration: Informational only - can be archived or removed in pure Ansible environment

- **index.html**: Static HTML test file for website verification
  - Migration: No change required - static asset

- **README.md files**: Documentation for the chef-examples repository and chef-and-ansible integration guide
  - Migration: Update to reflect Ansible-native compliance testing approach

### Target Details

Based on the Ansible playbooks and Test Kitchen configuration:

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbooks)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver configuration)
- **Cloud Platform**: Not specified - configuration supports local development with Vagrant or could be adapted for cloud deployment

## Migration Approach

### Key Dependencies to Address

**Test and Verification Tools:**
- **Chef InSpec**: Replace with Ansible-native compliance testing solutions:
  - Option 1: ansible.builtin.assert with ansible.builtin.command/shell for system checks
  - Option 2: community.crypto.openssl_certificate_info for SSL validation
  - Option 3: ansible.builtin.uri module for HTTP/HTTPS endpoint testing
  - Option 4: Retain Chef InSpec as external scanner (not recommended for full migration)

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing:
  - molecule init scenario --driver-name vagrant
  - Migrate verifier from InSpec to Ansible testinfra or native Molecule verifiers
  - Preserve Ubuntu 20.04 platform specification

**Ansible Collections (Already in use, ensure latest versions):**
- community.crypto: For OpenSSL operations (already used in website_https.yml)
- ansible.posix: For advanced system configuration

### Security Considerations

**Certificate and Key Management:**
- The website_https playbook generates self-signed certificates suitable for testing
- Migration consideration: Ensure certificate generation follows organizational security policies
- For production: Replace self-signed certificates with proper CA-signed certificates or Let's Encrypt integration
- Certificate files stored in /etc/apache2/certs/ with mode 0640 - verify permissions meet security requirements

**SSH Security:**
- ssh_profile InSpec test enforces STIG requirement for PermitRootLogin disabled
- Migration approach: Convert to Ansible assert task or integrate with ansible-lockdown STIG role
- Ensure new compliance tests maintain CAT I severity validation

**Hardcoded Credentials in Deployment Scripts:**
- setup-automate/deploy-automate.sh contains hardcoded passwords (userpassword='password')
- setup-automate/deploy-chef-server.sh contains hardcoded passwords (userpassword='password')
- Migration approach: If deployment scripts are retained, migrate to Ansible playbooks with ansible-vault encrypted variables
- Recommendation: These scripts are specific to Chef infrastructure and should be archived rather than migrated

**SSL/TLS Protocol Enforcement:**
- poodle_fix.yml enforces TLS 1.2 only by modifying Apache SSL configuration
- Verify current security requirements - TLS 1.3 may be preferred for new deployments
- Migration: Already in Ansible format, but review protocol versions for current standards

### Technical Challenges

**Challenge 1: InSpec to Ansible Test Conversion**
- **Description**: Chef InSpec provides rich compliance testing DSL that doesn't have direct Ansible equivalents
- **Mitigation Strategy**: 
  - Create custom Ansible task files for compliance verification using assert module
  - Consider ansible-test for syntax and integration testing
  - Evaluate testinfra (Python-based infrastructure testing) as InSpec alternative
  - Document test coverage matrix to ensure no compliance checks are lost in translation

**Challenge 2: Test Kitchen to Molecule Migration**
- **Description**: Different configuration syntax and workflow between Test Kitchen and Molecule
- **Mitigation Strategy**:
  - Create molecule.yml with equivalent Vagrant driver configuration
  - Map Test Kitchen suites to Molecule scenarios
  - Preserve platform specifications (Ubuntu 20.04)
  - Update CI/CD pipelines to use Molecule commands instead of Kitchen commands

**Challenge 3: Loss of InSpec Reporting Capabilities**
- **Description**: Chef InSpec provides detailed compliance reports with STIG mappings, CCI references, and severity ratings
- **Mitigation Strategy**:
  - If compliance reporting is critical, consider retaining InSpec as external scanner
  - Investigate Ansible compliance automation tools (ansible-lockdown, OpenSCAP integration)
  - Create custom reporting module using ansible-runner output
  - Evaluate if Chef Automate is being retained for compliance visibility

**Challenge 4: STIG Compliance Maintenance**
- **Description**: ssh_profile contains specific STIG control mappings (RHEL-08-000227, V-38607) that must be preserved
- **Mitigation Strategy**:
  - Use ansible-lockdown/RHEL8-STIG role from Ansible Galaxy for comprehensive STIG compliance
  - Document STIG control mappings in Ansible playbook comments
  - Create compliance validation playbooks that can be run independently
  - Maintain traceability between old InSpec controls and new Ansible tasks

### Migration Order

This repository has minimal migration complexity since it's already Ansible-based. Recommended order:

1. **Documentation and Planning** (Priority 1 - 1 day)
   - Document current InSpec test coverage
   - Map InSpec controls to Ansible equivalent tests
   - Create test coverage matrix

2. **Test Infrastructure Migration** (Priority 2 - 2-3 days)
   - Set up Molecule with Vagrant driver
   - Create initial molecule.yml mirroring kitchen.yml configuration
   - Validate Molecule can provision and test playbooks

3. **Compliance Test Conversion** (Priority 3 - 2-3 days)
   - Convert website_https_verify.rb to Ansible verification tasks
   - Convert ssh_profile.rb to Ansible compliance checks
   - Implement alternative STIG compliance validation
   - Create verify.yml playbook for Molecule

4. **Integration and Validation** (Priority 4 - 2-3 days)
   - Run full Molecule test cycle (create, converge, verify, destroy)
   - Compare test results between InSpec and Ansible verification
   - Update CI/CD pipelines
   - Documentation updates

5. **Cleanup and Archival** (Priority 5 - 1 day)
   - Archive Chef-specific deployment scripts (setup-automate directory)
   - Remove Test Kitchen configuration after Molecule validation
   - Update README files with new testing procedures

### Assumptions

1. **InSpec Removal is Desired**: Assuming the goal is to eliminate all Chef dependencies including InSpec. If InSpec compliance scanning should be retained for regulatory/audit purposes, this changes the migration scope significantly.

2. **Test Coverage Equivalence**: Assuming that Ansible-native testing can provide equivalent coverage to InSpec tests. Some InSpec resources (like `ssl()` resource) have rich built-in functionality that may require custom implementation in Ansible.

3. **Ubuntu 20.04 Platform Continuity**: Assuming Ubuntu 20.04 remains the target platform. If upgrading to Ubuntu 22.04 or RHEL 9 is desired, additional testing and package version updates will be required.

4. **Self-Signed Certificates Acceptable**: Assuming self-signed certificates are acceptable for the test/demo environment. Production deployments would require proper certificate management strategy.

5. **Vagrant Availability**: Assuming Vagrant and VirtualBox (or alternative provider) are available in the development environment for Molecule testing.

6. **No Chef Automate Dependency**: Assuming Chef Automate is not being used in the production environment for compliance reporting. If Automate is in use, consider retaining InSpec integration for consistent reporting.

7. **STIG Compliance Requirements**: Assuming STIG compliance validation must be maintained. The ssh_profile InSpec test references specific STIG controls that must be preserved in the migrated solution.

8. **CI/CD Pipeline Exists**: Assuming there is a CI/CD pipeline currently using Test Kitchen that will need updates to use Molecule. If no pipeline exists, this reduces migration complexity.

9. **No Hidden Chef Dependencies**: Based on the file search results, assuming there are no Chef cookbooks, recipes, or Chef client dependencies hidden in subdirectories not visible in the provided tree structure.

10. **Demonstration vs. Production**: Assuming this is demonstration/example code per the README. If this is production infrastructure, additional considerations for testing, rollback procedures, and change management would be required.

11. **Local Development Focus**: The repository appears focused on local development/testing with Vagrant. Assuming no immediate need for cloud provider-specific testing infrastructure.

12. **No Custom InSpec Resources**: Assuming the InSpec tests use only built-in InSpec resources. Custom resources would require additional analysis and custom Ansible module development.
