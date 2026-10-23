# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository presents an **unusual migration scenario**: it is a reference/demo repository that demonstrates using Chef InSpec for compliance testing alongside Ansible playbooks. The repository does **not** contain traditional Chef cookbooks requiring migration. Instead, it contains:

- **Ansible playbooks** (already in target format)
- **Chef InSpec test profiles** (compliance verification - can be retained)
- **Test Kitchen configuration** (integration testing framework)
- **Chef infrastructure deployment scripts** (server setup automation)

**Migration Scope**: Minimal. The Ansible playbooks are already written and functional. The primary work involves:
1. Replacing Test Kitchen with native Ansible testing tools (Molecule or ansible-test)
2. Deciding whether to retain Chef InSpec or migrate to Ansible compliance tools
3. Replacing Chef infrastructure deployment scripts with Ansible-native solutions

**Complexity**: Low (1-2 weeks)

**Timeline Estimate**:
- Testing framework migration: 3-5 days
- Documentation updates: 2-3 days
- Validation and verification: 2-3 days
- Total: 1-2 weeks

## Module Migration Plan

This repository does not contain Chef cookbooks in the traditional sense. It is a demonstration repository showing how Chef InSpec can complement Ansible for compliance automation.

### MODULE INVENTORY

**No Chef cookbooks requiring migration**. This repository contains:

1. **website_https (Ansible Playbook)**:
   - Description: Apache web server deployment with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for a Hello World test site
   - Path: chef-and-ansible/website_https.yml
   - Technology: Ansible (already migrated)
   - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module enablement

2. **poodle_fix (Ansible Playbook)**:
   - Description: SSL/TLS security hardening for Apache by disabling vulnerable SSL protocols and enforcing TLS 1.2
   - Path: chef-and-ansible/poodle_fix.yml
   - Technology: Ansible (already migrated)
   - Key Features: Apache SSL configuration remediation, protocol restriction to TLS 1.2, service restart handling

3. **website_https_verify (Chef InSpec Profile)**:
   - Description: Compliance verification tests for HTTPS functionality, SSL protocol security, and web server availability
   - Path: chef-and-ansible/tests/website_https_verify.rb
   - Technology: Chef InSpec
   - Key Features: Port 443 listening check, HTTPS response validation, SSL protocol verification (SSLv3 disabled, TLS 1.2 enabled)

4. **ssh_profile (Chef InSpec Profile)**:
   - Description: SSH security compliance profile ensuring root login is disabled per STIG requirements
   - Path: chef-and-ansible/tests/ssh_profile.rb
   - Technology: Chef InSpec
   - Key Features: STIG control V-38607 implementation, SSH configuration verification, CCI-000774 compliance

### Infrastructure Files

- **kitchen.yml**: Test Kitchen configuration for testing Ansible playbooks using Vagrant driver with Chef InSpec verifier. Uses Ubuntu 20.04 as test platform.

- **setup-automate/deploy-automate.sh**: Bash script for deploying Chef Automate and Chef Infra Server on VM infrastructure. Contains hardcoded credentials and organizational configuration.

- **setup-automate/deploy-chef-server.sh**: Bash script for standalone Chef Infra Server deployment without Automate. Similar configuration to deploy-automate.sh with infrastructure-specific settings.

- **index.html**: Static HTML test file for web server validation.

- **README.md files**: Documentation explaining the integration of Chef InSpec with Ansible for compliance automation.

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbook package versions)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen for local testing)
- **Cloud Platform**: Not specified; designed for on-premises or cloud VM deployment (scripts support generic VM infrastructure)

## Migration Approach

### Key Dependencies to Address

**Test Kitchen Dependencies**:
- **kitchen-vagrant**: Replace with Molecule using Vagrant or Docker driver for local testing
- **kitchen-ansible**: Replace with native Molecule Ansible provisioner
- **kitchen-inspec**: Decision point - retain InSpec or migrate to ansible-test/Molecule verify

**Chef InSpec**:
- **inspec (latest)**: Options:
  1. **Retain InSpec** as compliance verification tool (recommended for organizations already using InSpec)
  2. **Migrate to Ansible compliance tools**: ansible-lint for static analysis, custom test tasks for runtime validation
  3. **Adopt Ansible Molecule with testinfra**: Python-based testing as alternative to InSpec

**Chef Infrastructure**:
- **chef-automate**: No direct equivalent needed; deployment scripts are for Chef server infrastructure, not configuration management
- **chef-server-ctl**: Not needed in Ansible-only environment

**Ansible Dependencies** (already present):
- **ansible_playbook provisioner**: Already configured, no migration needed
- **openssl modules**: Python3-openssl already specified in playbooks

### Security Considerations

**Credentials Management**:
- **Hardcoded passwords in deployment scripts**: Both setup-automate scripts contain plaintext passwords (`userpassword='password'`). These must be:
  1. Migrated to Ansible Vault for secure variable storage
  2. Removed from version control history if repository will continue
  3. Replaced with environment variables or secrets management system

**SSL/TLS Certificate Management**:
- **Self-signed certificates**: Current playbooks generate self-signed certificates. Production migration should:
  1. Integrate with certificate authority (Let's Encrypt via certbot, or internal CA)
  2. Implement certificate rotation automation
  3. Add certificate expiration monitoring

**STIG Compliance**:
- **SSH root login controls**: InSpec profile verifies STIG V-38607. Ensure Ansible playbooks include:
  1. SSH hardening tasks (currently only verified, not configured)
  2. Idempotent configuration management for all STIG controls
  3. Compliance-as-code integration with Ansible roles

**Service Credentials**:
- No database passwords, API keys, or service account credentials detected in reviewed files
- Future implementations should use Ansible Vault or external secrets management (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault)

### Technical Challenges

**1. Testing Framework Migration**:
- **Challenge**: Test Kitchen with InSpec verifier provides robust integration testing. Native Ansible testing tools have different paradigms.
- **Mitigation**: 
  1. Adopt Molecule with Ansible driver for testing
  2. Retain InSpec as Molecule verifier if compliance testing is critical
  3. Create Molecule scenarios replicating current Test Kitchen suites
  4. Document testing approach for team consistency

**2. InSpec Profile Decision**:
- **Challenge**: Organization may have significant investment in InSpec profiles and expertise.
- **Mitigation**:
  1. **If retaining InSpec**: Integrate via Molecule verifier or ansible-inspec module
  2. **If migrating away**: Convert InSpec controls to Ansible assert tasks or testinfra tests
  3. **Hybrid approach**: Use InSpec for compliance verification, Ansible for configuration management
  4. Maintain compliance profile library regardless of testing tool

**3. Chef Infrastructure Decommissioning**:
- **Challenge**: Setup scripts deploy Chef servers. Organization may have existing Chef infrastructure to migrate away from.
- **Mitigation**:
  1. Identify all systems still managed by Chef
  2. Create parallel Ansible inventory for those systems
  3. Gradually migrate node management from Chef to Ansible
  4. Plan Chef server decommissioning timeline (not just this repository)

**4. Compliance Automation Gap**:
- **Challenge**: Current setup verifies compliance but doesn't enforce it. InSpec tests check SSH hardening but playbooks don't configure it.
- **Mitigation**:
  1. Create complementary Ansible roles for each InSpec profile
  2. Implement remediation playbooks that fix detected compliance failures
  3. Adopt test-driven infrastructure: write InSpec/compliance tests first, then Ansible implementation
  4. Integrate compliance scanning into CI/CD pipeline

### Migration Order

This repository requires minimal migration since Ansible playbooks already exist. Recommended order:

1. **Testing Framework Setup** (Priority: High, Complexity: Low)
   - Install and configure Molecule
   - Create molecule.yml scenarios replicating kitchen.yml suites
   - Validate Molecule can execute existing playbooks
   - Document testing workflow for team

2. **InSpec Integration Decision** (Priority: High, Complexity: Medium)
   - Evaluate organizational commitment to InSpec
   - If retaining: Configure Molecule with InSpec verifier
   - If migrating: Begin converting InSpec controls to alternative testing framework
   - Establish compliance testing standards

3. **Security Hardening** (Priority: High, Complexity: Low)
   - Remove hardcoded credentials from deployment scripts
   - Implement Ansible Vault for sensitive variables
   - Create secure variable management documentation
   - Audit repository history for exposed secrets

4. **Compliance Remediation Playbooks** (Priority: Medium, Complexity: Medium)
   - Create SSH hardening role based on ssh_profile.rb requirements
   - Develop SSL/TLS hardening role beyond current poodle_fix
   - Implement STIG compliance roles matching InSpec profiles
   - Integrate remediation into main playbooks

5. **Documentation Updates** (Priority: Medium, Complexity: Low)
   - Update README files to remove Chef cookbook references
   - Document Ansible-native testing approach
   - Create runbooks for common operations
   - Establish contribution guidelines for Ansible development

6. **Chef Infrastructure Migration** (Priority: Low, Complexity: N/A for this repo)
   - This repository doesn't require Chef server infrastructure
   - If broader organization migration: plan separately from this repository
   - Archive or remove setup-automate scripts once Chef is decommissioned

### Assumptions

1. **Repository Purpose**: This appears to be a demonstration/reference repository, not production infrastructure code. Migration urgency and approach may differ for reference vs. production repositories.

2. **InSpec Organizational Investment**: The plan assumes the organization may have broader Chef InSpec usage beyond this repository. If InSpec is only present in this demo repo, full migration to Ansible-native testing would be simpler.

3. **Chef Infrastructure Status**: The deployment scripts suggest a Chef server infrastructure may exist. The migration plan assumes this is being decommissioned as part of the broader Chef-to-Ansible migration, but timeline is unclear.

4. **Testing Requirements**: The plan assumes robust testing is required (based on Test Kitchen presence). If this is a simple demo without CI/CD requirements, testing framework migration may be optional.

5. **Compliance Requirements**: The presence of STIG-referenced InSpec profiles suggests a compliance-focused environment. The plan assumes compliance automation must be maintained or improved during migration.

6. **Operating System Scope**: All playbooks target Ubuntu 20.04. The plan assumes this is the primary or only target OS. Multi-OS support would increase migration complexity.

7. **Team Expertise**: The plan assumes the team has Ansible experience (since playbooks already exist) but may need training on Molecule, InSpec integration, or other testing frameworks.

8. **CI/CD Integration**: The Test Kitchen configuration suggests automated testing. The plan assumes equivalent CI/CD integration will be required for the Ansible testing approach.

9. **Secrets Management Maturity**: Hardcoded credentials in scripts suggest limited secrets management infrastructure. The plan assumes Ansible Vault is acceptable as initial solution, with potential future migration to enterprise secrets management.

10. **Production Usage**: It's unclear if the Ansible playbooks in this repository are used in production or are purely demonstrative. Migration priority and testing rigor should adjust accordingly.

11. **Apache Version Lock**: The playbook specifies exact Apache version `2.4.41-4ubuntu3.10`. This suggests either a compliance requirement or potential brittleness if that package version is no longer available in repositories.

12. **Certificate Management Evolution**: Self-signed certificates are acceptable for current use case. Production migration may require integration with organizational PKI or public certificate authorities.

## Recommended Next Steps

1. **Clarify Repository Purpose**: Determine if this is a reference repository or production infrastructure code to appropriately scope migration effort.

2. **InSpec Strategy Session**: Conduct stakeholder meeting to decide InSpec retention vs. migration to alternative compliance tools.

3. **Molecule Proof of Concept**: Create initial Molecule configuration for one playbook to validate approach and identify gaps.

4. **Security Audit**: Review full repository history for exposed credentials; rotate any found credentials immediately.

5. **Compliance Gap Analysis**: Identify all InSpec controls that lack corresponding Ansible remediation and prioritize implementation.

6. **Team Training Plan**: Assess team's familiarity with Molecule, Ansible testing best practices, and compliance-as-code approaches; plan training accordingly.
