# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance tests and Ansible playbooks demonstrating hybrid automation approaches. The migration scope is limited as this is primarily a demonstration repository showing Chef InSpec integration with Ansible rather than traditional Chef cookbooks requiring migration. The primary migration effort involves consolidating the compliance testing into native Ansible approaches while preserving the existing Ansible automation.

## Module Migration Plan

This repository contains Chef InSpec compliance tests and supporting infrastructure that need individual migration planning:

### MODULE INVENTORY

**website-https-compliance**:
- Description: Apache HTTPS web server deployment with SSL/TLS configuration, self-signed certificate generation, and compliance verification
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, compliance testing via InSpec

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening to disable SSLv3 and enforce TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handlers

**ssh-security-compliance**:
- Description: SSH security compliance verification ensuring root login is disabled per security standards
- Path: chef-and-ansible/tests/ssh_profile.rb
- Technology: Chef InSpec
- Key Features: STIG compliance (RHEL-08-000227), SSH configuration validation, security control verification

**https-service-compliance**:
- Description: HTTPS service availability and SSL protocol compliance verification
- Path: chef-and-ansible/tests/website_https_verify.rb
- Technology: Chef InSpec
- Key Features: Port 443 listening verification, HTTP 200 response validation, SSL protocol compliance testing

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `index.html`: Static web content for demonstration purposes
- `deploy-automate.sh`: Chef Automate and Infra Server deployment script for lab environments
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (as specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with ansible-lint, molecule testing, or native Ansible assert modules
- **Test Kitchen**: Replace with Molecule for Ansible testing framework
- **Vagrant Driver**: Maintain existing Vagrant integration or migrate to container-based testing

### Security Considerations
- **SSL/TLS Configuration**: Existing Ansible playbooks already implement proper SSL hardening
  - Self-signed certificate generation via OpenSSL modules
  - TLS 1.2 enforcement and SSLv3 disabling
  - Proper file permissions (0640) for certificate directories
- **SSH Hardening**: InSpec test validates PermitRootLogin disabled - migrate to Ansible assert or lineinfile verification
- **Compliance Standards**: STIG controls (RHEL-08-000227) need native Ansible validation approach
- **Credential Management**: No hardcoded credentials detected - uses variables and generated certificates

### Technical Challenges
- **InSpec Test Migration**: Converting Chef InSpec compliance tests to native Ansible verification
  - Port listening checks can use wait_for module
  - HTTP response validation can use uri module with assert
  - SSL protocol verification requires custom validation or external tools
- **Test Framework Transition**: Moving from Test Kitchen to Molecule for comprehensive testing
- **Compliance Reporting**: InSpec provides structured compliance reporting - need equivalent Ansible solution

### Migration Order
1. **Ansible Playbook Validation** (already complete - playbooks are native Ansible)
2. **InSpec Test Conversion** (moderate complexity - convert to Ansible assert/uri modules)
3. **Test Framework Migration** (low complexity - replace Test Kitchen with Molecule)
4. **Documentation Updates** (low complexity - update README and examples)

### Assumptions
- Target environment remains Ubuntu 20.04 LTS as specified in existing configuration
- Vagrant-based testing approach will be maintained or replaced with container-based alternatives
- Compliance requirements (STIG controls) must be preserved in native Ansible format
- Self-signed certificates are acceptable for demonstration purposes (production would require CA-signed certificates)
- Apache 2.4.41 version pinning is intentional for demonstration consistency
- SSH security hardening requirements remain unchanged from current InSpec specifications
- Test Kitchen integration can be replaced with Molecule without loss of functionality
- Chef Automate deployment scripts are for lab setup only and not part of production migration scope