# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance tests and Ansible playbooks demonstrating integration between Chef InSpec and Ansible for compliance automation. The migration scope is limited as this is primarily a demonstration repository with existing Ansible playbooks and InSpec tests, rather than traditional Chef cookbooks requiring full migration.

**Migration Complexity**: Low  
**Estimated Timeline**: 1-2 weeks  
**Primary Focus**: InSpec test conversion to Ansible compliance modules

## Module Migration Plan

This repository contains Chef InSpec compliance tests and supporting infrastructure that demonstrate integration with Ansible:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
This repository does not contain traditional Chef cookbooks with recipes. Instead, it contains InSpec compliance tests and Ansible playbooks for demonstration purposes.

**InSpec Compliance Tests:**
- **website_https_verify**:
    - Description: InSpec compliance tests for HTTPS website verification, SSL protocol validation, and port accessibility checks
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port 443 listening verification, HTTPS response validation, SSL/TLS protocol compliance (disables SSL3, enables TLS1.2)

- **ssh_profile**:
    - Description: InSpec compliance profile for SSH security hardening with STIG compliance controls
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login prohibition, STIG control SRG-OS-000112 compliance, audit trail requirements

**Ansible Playbooks (Already Present):**
- **website_https**:
    - Description: Ansible playbook for Apache HTTPS website deployment with SSL certificate generation
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache 2.4.41 installation, self-signed SSL certificate creation, virtual host configuration, SSL module activation

- **poodle_fix**:
    - Description: Ansible playbook for SSL security hardening to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol restriction to TLS 1.2 only, Apache SSL configuration updates

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible provisioner with InSpec verifier integration
- `index.html`: Static HTML test content for website deployment verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible compliance modules (ansible.posix.sysctl, community.general.apache2_module)
- **Test Kitchen**: Replace with Molecule for Ansible testing framework
- **Chef Automate/Server**: Remove dependency as InSpec tests will be converted to native Ansible compliance checks

### Security Considerations
- **SSL/TLS Configuration**: Current InSpec tests validate SSL protocol restrictions - migrate to Ansible template validation and configuration management
- **SSH Hardening**: Convert STIG-compliant SSH controls to Ansible security role with built-in compliance validation
- **Certificate Management**: Existing Ansible playbook uses self-signed certificates - consider integration with Let's Encrypt or enterprise CA for production
- **Credential Management**: No hardcoded credentials detected in current implementation - maintain this security posture in migrated solution

### Technical Challenges
- **InSpec to Ansible Compliance Conversion**: InSpec's declarative compliance testing model needs translation to Ansible's imperative configuration management with validation tasks
- **STIG Control Mapping**: SSH profile contains specific STIG controls (SRG-OS-000112, V-38607) that require mapping to equivalent Ansible security role controls
- **Test Framework Migration**: Test Kitchen + InSpec workflow needs replacement with Molecule + Ansible testing approach
- **Compliance Reporting**: InSpec's compliance reporting capabilities need equivalent implementation using Ansible facts gathering and reporting modules

### Migration Order
1. **InSpec Test Conversion** (Priority 1 - foundational): Convert InSpec compliance tests to Ansible validation tasks and security roles
2. **Test Framework Migration** (Priority 2 - development workflow): Replace Test Kitchen with Molecule for Ansible testing
3. **Infrastructure Cleanup** (Priority 3 - optional): Remove Chef Automate deployment scripts if no longer needed for demonstration

### Assumptions
- The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already functional and do not require migration - they serve as the target state
- InSpec compliance tests need conversion to Ansible native compliance validation rather than full cookbook migration
- Test Kitchen configuration suggests this is a development/demonstration environment rather than production infrastructure
- Chef Automate/Server deployment scripts may be retained for demonstration purposes or removed if focusing purely on Ansible
- Ubuntu 20.04 target platform will be maintained in the migrated solution
- Self-signed certificate approach is acceptable for demonstration purposes but should be enhanced for production use
- STIG compliance requirements (specifically SRG-OS-000112) must be maintained in the migrated Ansible solution
- The repository serves as a reference implementation rather than production infrastructure requiring migration