# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible playbooks, rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks with Chef InSpec test verification, along with Chef Automate deployment scripts. The migration scope is minimal as the infrastructure automation is already implemented in Ansible - the focus should be on replacing Chef InSpec testing with native Ansible testing approaches.

## Module Migration Plan

This repository contains demonstration/example code rather than production infrastructure modules:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Ansible playbook demonstrating Apache HTTPS website deployment with SSL certificate generation and Chef InSpec compliance testing
- Path: chef-and-ansible/
- Technology: Ansible (with Chef InSpec testing)
- Key Features: Apache 2.4 installation, self-signed SSL certificate generation, virtual host configuration, POODLE vulnerability mitigation, Test Kitchen integration

**setup-automate**:
- Description: Bash deployment scripts for Chef Automate and Chef Infra Server installation and initial configuration
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `website_https.yml`: Main Ansible playbook for Apache HTTPS site deployment
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disables SSLv3, enables TLS 1.2)
- `tests/website_https_verify.rb`: Chef InSpec tests for HTTPS functionality and SSL protocol compliance
- `tests/ssh_profile.rb`: Chef InSpec control for SSH root login security verification
- `deploy-automate.sh`: Chef Automate and Infra Server deployment automation
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified (examples designed for generic VM deployment)

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with ansible-lint, molecule testing, or native Ansible assert modules
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and verification
- **Chef Automate/Server**: Evaluate need for centralized configuration management - consider AWX/Ansible Tower or native Ansible automation

### Security Considerations
- SSL/TLS certificate management: Current implementation uses self-signed certificates - consider integration with Let's Encrypt or enterprise CA
- SSH hardening verification: Migrate InSpec SSH controls to Ansible security role or custom verification tasks
- Apache security configuration: POODLE fix demonstrates security hardening - ensure equivalent controls in migrated playbooks
- Credential management: Deployment scripts contain hardcoded passwords - implement Ansible Vault for secrets management

### Technical Challenges
- **Testing Framework Migration**: Replace Chef InSpec testing with Ansible-native testing approaches (molecule, testinfra, or custom verification tasks)
- **Compliance Verification**: Migrate InSpec compliance controls to Ansible security roles or custom compliance modules
- **Infrastructure Validation**: Replace Test Kitchen workflow with Molecule for comprehensive playbook testing
- **Chef Ecosystem Removal**: Eliminate dependency on Chef Automate/Server if not required for other organizational needs

### Migration Order
1. **Apache HTTPS Playbook** (low risk, already in Ansible format - focus on testing migration)
2. **SSL Security Hardening** (moderate complexity, security-critical configuration)
3. **Testing Framework** (high complexity, requires new tooling and process establishment)

### Assumptions
- This repository serves as example/demonstration code rather than production infrastructure requiring migration
- The organization may be evaluating Chef InSpec integration with Ansible rather than planning a full Chef-to-Ansible migration
- Test Kitchen and Chef InSpec knowledge exists within the team for the testing framework migration
- The Apache HTTPS deployment represents a pattern that may be replicated across other services requiring similar migration approach
- Chef Automate/Server deployment scripts suggest potential broader Chef ecosystem usage that may require separate migration planning
- Ubuntu/Debian package management approach may need adaptation for RHEL/CentOS target environments
- Self-signed certificate approach is acceptable for development/testing but production deployment will require proper certificate management integration