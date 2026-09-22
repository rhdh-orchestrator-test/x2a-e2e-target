# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains demonstration examples for using Chef InSpec alongside Ansible for compliance automation, rather than traditional Chef cookbooks. The migration scope is limited as the repository primarily contains Ansible playbooks with InSpec tests for validation. The main migration effort involves replacing Chef InSpec tests with native Ansible testing approaches and consolidating the Chef Automate deployment scripts into Ansible automation.

**Timeline Estimate**: 1-2 weeks for a small team
**Complexity**: Low to Medium - primarily involves test framework migration and infrastructure automation

## Module Migration Plan

This repository contains Chef InSpec compliance tests and Ansible demonstration content that need migration planning:

### MODULE INVENTORY

**website-https-compliance**:
- Description: Apache HTTPS website deployment with SSL/TLS configuration, self-signed certificate generation, and compliance validation
- Path: chef-and-ansible/
- Technology: Ansible playbooks with Chef InSpec tests
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, POODLE vulnerability mitigation (TLS 1.2 enforcement)

**ssh-security-compliance**:
- Description: SSH security hardening compliance test ensuring root login is disabled per security benchmarks
- Path: chef-and-ansible/tests/ssh_profile.rb
- Technology: Chef InSpec
- Key Features: STIG compliance (RHEL-08-000227), root login prevention, security control validation with CAT I severity rating

**chef-infrastructure-deployment**:
- Description: Chef Automate and Chef Infra Server deployment automation for on-premises or cloud environments
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate installation, Chef Infra Server setup, user and organization provisioning, system tuning (vm.max_map_count, vm.dirty_expire_centisecs)

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `website_https.yml`: Ansible playbook for Apache HTTPS setup with SSL certificate management
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disabling SSL 3.0, enforcing TLS 1.2)
- `deploy-automate.sh`: Chef Automate deployment script with system configuration
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with RHEL compatibility for SSH security controls
- **Virtual Machine Technology**: Vagrant with VirtualBox (Test Kitchen configuration)
- **Cloud Platform**: Cloud-agnostic deployment scripts support on-premises and cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible native testing using ansible-test, molecule, or testinfra
- **Test Kitchen**: Migrate to Molecule for Ansible role testing and validation
- **Chef Automate/Server**: Replace with Ansible AWX/Tower or native Ansible automation for infrastructure deployment
- **OpenSSL Ansible modules**: Already using python3-openssl, no migration needed

### Security Considerations
- **SSL/TLS Configuration**: Current implementation uses self-signed certificates - consider integration with Let's Encrypt or proper CA for production
- **SSH Hardening**: InSpec test validates PermitRootLogin=no - ensure Ansible playbooks maintain this security posture
- **STIG Compliance**: SSH profile implements RHEL-08-000227 control - migrate compliance validation to Ansible-native security scanning
- **Credential Management**: Chef server deployment scripts contain hardcoded credentials (username, password, email) - migrate to Ansible Vault or external secret management
- **Certificate Storage**: SSL certificates stored in /etc/apache2/certs with 0640 permissions - maintain secure file permissions in Ansible implementation

### Technical Challenges
- **InSpec Test Migration**: Converting Ruby-based InSpec tests to Ansible native testing frameworks requires syntax translation and validation logic adaptation
- **Compliance Framework Integration**: STIG controls and security benchmarks need mapping to Ansible security roles or custom validation tasks
- **Test Kitchen Replacement**: Migrating Vagrant-based testing workflow to Molecule requires infrastructure-as-code test environment reconfiguration
- **Chef Infrastructure Dependencies**: Removing Chef Automate deployment dependencies while maintaining equivalent monitoring and compliance capabilities

### Migration Order
1. **website-https-compliance** (low risk, self-contained Ansible playbook with minimal Chef dependencies)
2. **ssh-security-compliance** (moderate complexity, requires InSpec test conversion to Ansible validation)
3. **chef-infrastructure-deployment** (high complexity, requires complete replacement of Chef-specific infrastructure)

### Assumptions
- Target environment will use Ansible AWX/Tower instead of Chef Automate for automation orchestration
- Compliance validation will migrate from InSpec to Ansible-native testing frameworks (molecule, testinfra, or custom validation tasks)
- SSL certificate management will continue using self-signed certificates for testing, with option to integrate proper CA or Let's Encrypt for production
- SSH security hardening requirements remain consistent with current STIG compliance standards
- Test Kitchen workflow will be replaced with Molecule for role testing and validation
- Chef server deployment functionality will be replaced with equivalent Ansible automation for infrastructure provisioning
- Hardcoded credentials in deployment scripts will be externalized to Ansible Vault or secret management systems
- Ubuntu 20.04 target environment is acceptable, with RHEL compatibility maintained for security controls