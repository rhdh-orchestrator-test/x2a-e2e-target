# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository is a demonstration project showing Chef InSpec integration with Ansible for compliance automation. The migration scope is minimal as the core infrastructure automation is already implemented in Ansible. The primary migration task involves replacing Chef InSpec compliance testing with native Ansible testing solutions.

**Migration Complexity**: Low  
**Estimated Timeline**: 1-2 weeks  
**Risk Level**: Low

## Module Migration Plan

This repository contains demonstration examples and deployment scripts rather than production Chef cookbooks requiring migration:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS security hardening, and virtual host setup
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, SSL virtual host configuration, security hardening

**poodle-vulnerability-fix**:
- Description: Ansible playbook for SSL/TLS protocol hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL configuration updates, protocol restriction, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible native testing modules (ansible.builtin.uri, ansible.builtin.assert, community.crypto.openssl_certificate_info)
- **Test Kitchen**: Replace with molecule for Ansible playbook testing
- **Chef Automate/Server**: Remove deployment scripts as they are not needed for pure Ansible infrastructure

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks already implement proper SSL hardening practices
  - Self-signed certificate generation using community.crypto modules
  - TLS 1.2 enforcement and SSLv3 disabling
  - Proper certificate file permissions (0640)
- **SSH Security**: InSpec test validates SSH root login restrictions - migrate to Ansible assert tasks
- **Credential Management**: No hardcoded credentials detected in current playbooks
  - Variables are properly externalized
  - Certificate keys are generated dynamically

### Technical Challenges

- **InSpec Test Migration**: Convert Ruby-based InSpec tests to Ansible native verification tasks
  - Port 443 listening check: Use ansible.builtin.wait_for module
  - HTTPS response validation: Use ansible.builtin.uri module with status code assertions
  - SSL protocol verification: Use community.crypto.openssl_certificate_info module
- **Test Kitchen Replacement**: Migrate from Test Kitchen to Molecule for comprehensive playbook testing
- **Compliance Reporting**: Replace InSpec compliance reports with Ansible custom reporting or integration with external compliance tools

### Migration Order

1. **InSpec Test Conversion** (Priority 1 - Low complexity, high value)
   - Convert website_https_verify.rb to Ansible verification tasks
   - Convert ssh_profile.rb to Ansible SSH configuration validation
2. **Test Framework Migration** (Priority 2 - Moderate complexity)
   - Replace Test Kitchen with Molecule configuration
   - Update CI/CD pipelines to use Molecule instead of kitchen commands
3. **Documentation Updates** (Priority 3 - Low complexity)
   - Update README files to reflect pure Ansible approach
   - Remove Chef-specific references and deployment scripts

### Assumptions

- The current Ansible playbooks are demonstration/example code and not production-critical infrastructure
- The organization is moving away from Chef ecosystem entirely, including InSpec for compliance testing
- Test Kitchen and Chef deployment scripts can be completely removed rather than maintained
- The target environment will continue to use Ubuntu 20.04 or can be easily updated to newer versions
- Molecule testing framework is acceptable as a replacement for Test Kitchen
- Native Ansible testing capabilities are sufficient for the compliance requirements currently met by InSpec
- The SSL/TLS security requirements remain the same (TLS 1.2 minimum, SSLv3 disabled)
- SSH security policies (root login disabled) remain unchanged
- Self-signed certificates are acceptable for the demonstration environment (production would require proper CA-signed certificates)