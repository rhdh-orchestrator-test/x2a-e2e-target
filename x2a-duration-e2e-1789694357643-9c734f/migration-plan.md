# MIGRATION FROM MIXED ANSIBLE/CHEF INSPEC TO ANSIBLE

This repository contains example Ansible playbooks with Chef InSpec compliance testing and Chef infrastructure deployment scripts. **This is not a traditional migration scenario** - the repository already contains Ansible playbooks and serves as a demonstration of using Chef InSpec alongside Ansible for compliance automation. The migration focus should be on consolidating to pure Ansible solutions and replacing Chef InSpec with Ansible-native compliance tools.

## Module Migration Plan

This repository contains demonstration content rather than production infrastructure modules:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
The following components were identified from the actual repository structure:

- **website-https-demo**:
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS security hardening, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, SSL virtual host configuration, security hardening

- **poodle-ssl-fix**:
    - Description: Ansible playbook for SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 (POODLE vulnerability mitigation)
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration replacement, TLS protocol enforcement, service restart handling

- **compliance-testing-framework**:
    - Description: Chef InSpec compliance tests for HTTPS functionality, SSL protocol validation, and SSH security controls
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port 443 listening verification, HTTPS response validation, SSL protocol compliance (SSLv3 disabled, TLS 1.2 enabled), SSH root login security control (STIG compliance)

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification in Vagrant environment
- `deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script with user/org provisioning
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content for web server validation
- `README.md`: Documentation explaining the Chef InSpec + Ansible compliance automation approach

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible-native compliance testing using ansible-lint, molecule, or custom validation tasks
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and validation
- **Chef Automate/Server**: Eliminate dependency on Chef infrastructure components

### Security Considerations
- **SSL/TLS Configuration**: Current playbooks demonstrate proper SSL hardening practices that should be maintained
  - Self-signed certificate generation using OpenSSL modules
  - SSL protocol enforcement (TLS 1.2 minimum)
  - Apache SSL module configuration
- **SSH Security Controls**: InSpec tests validate SSH root login restrictions (STIG compliance)
- **Credential Management**: No hardcoded credentials identified - deployment scripts use variables for user configuration
- **Certificate Management**: Self-signed certificates used for demonstration - production migration should integrate with proper CA or certificate management solution

### Technical Challenges
- **Compliance Testing Migration**: Converting Chef InSpec tests to Ansible-native validation requires:
  - Replacing InSpec controls with Ansible assert tasks or custom validation modules
  - Maintaining STIG compliance validation capabilities
  - Preserving detailed compliance reporting functionality
- **Test Framework Replacement**: Migrating from Test Kitchen to Molecule requires:
  - Reconfiguring test scenarios and platforms
  - Adapting verification steps to Molecule's testing approach
  - Maintaining integration with CI/CD pipelines

### Migration Order
1. **Compliance Testing Framework** (immediate priority - convert InSpec tests to Ansible validation tasks)
2. **Test Infrastructure** (replace Test Kitchen with Molecule for consistent testing)
3. **Documentation Updates** (update examples to reflect pure Ansible approach)

### Assumptions
- This repository serves as demonstration/example content rather than production infrastructure
- The goal is to showcase pure Ansible compliance automation without Chef dependencies
- Current Ansible playbooks are already well-structured and follow best practices
- Ubuntu 20.04 target platform will be maintained for consistency with existing examples
- Self-signed certificates are acceptable for demonstration purposes
- STIG compliance requirements must be preserved in the migrated validation approach
- Test Kitchen integration may be required to maintain compatibility with existing CI/CD processes during transition period