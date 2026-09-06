# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and demonstration materials that showcase integration between Chef InSpec and Ansible for compliance automation. The migration scope is limited as this is primarily an educational/demonstration repository rather than production infrastructure code. The main migration effort involves consolidating the existing Ansible playbooks and Chef InSpec tests into a cohesive Ansible-native compliance framework.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low (demonstration code, no production dependencies)

## Module Migration Plan

This repository contains demonstration materials and example configurations that showcase Chef InSpec integration with Ansible:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificate generation, and virtual host management for a simple "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL, Apache virtual host configuration, directory structure creation, service management with handlers

**ssl-security-hardening**:
- Description: SSL/TLS security hardening configuration that disables vulnerable SSL protocols and enforces TLS 1.2+ for Apache
- Path: chef-and-ansible/poodle_fix.yml  
- Technology: Ansible (already migrated)
- Key Features: POODLE vulnerability mitigation, SSL protocol configuration via regex replacement, service restart handlers

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `chef-and-ansible/index.html`: Static HTML content for website testing
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, SSL protocol verification, and port accessibility
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG control)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for lab environments
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **apache2 (2.4.41-4ubuntu3.10)**: Already using Ansible apt module for package management
- **openssl**: Already using Ansible openssl_* modules for certificate management
- **python3-openssl**: Already specified as dependency for Ansible OpenSSL modules
- **Test Kitchen**: Replace with Ansible Molecule for testing framework
- **Chef InSpec**: Integrate with ansible-lint and Ansible compliance scanning

### Security Considerations

- **SSL Certificate Management**: Currently uses self-signed certificates generated via Ansible OpenSSL modules - consider implementing proper certificate authority or Let's Encrypt integration
- **Hardcoded Credentials**: 
  - setup-automate scripts contain plaintext passwords and user credentials
  - No vault or secrets management detected in current Ansible playbooks
  - SSH configuration compliance testing via InSpec controls
- **SSL/TLS Security**: POODLE vulnerability mitigation already implemented via protocol restriction
- **File Permissions**: Proper file modes specified for certificate files (0640) and web content (0644/0755)

### Technical Challenges

- **InSpec Integration**: Current workflow uses Chef InSpec for compliance testing alongside Ansible - need to evaluate Ansible-native compliance solutions or maintain hybrid approach
- **Test Kitchen Replacement**: Migration from Test Kitchen to Ansible Molecule for testing infrastructure
- **Chef Server Dependencies**: Setup scripts deploy Chef infrastructure that may not be needed in pure Ansible environment
- **Compliance Framework**: SSH security controls (STIG-based) currently implemented in InSpec - need Ansible equivalent or maintain InSpec integration

### Migration Order

1. **apache-https-website** (already complete - Ansible native)
2. **ssl-security-hardening** (already complete - Ansible native)  
3. **Testing Framework Migration** (Test Kitchen → Ansible Molecule)
4. **Compliance Integration** (InSpec → Ansible compliance modules or hybrid approach)
5. **Infrastructure Setup** (evaluate need for Chef server deployment scripts)

### Assumptions

- This repository serves as demonstration/educational material rather than production infrastructure
- The existing Ansible playbooks are already functional and represent the target state
- InSpec compliance tests may need to be maintained alongside Ansible for comprehensive security validation
- Test Kitchen configuration suggests local development environment rather than production deployment
- Chef server deployment scripts may be retained for comparison/educational purposes rather than migrated
- Ubuntu 20.04 target platform is acceptable for demonstration purposes
- Self-signed certificates are sufficient for testing/demonstration scenarios
- No external Chef cookbooks or complex dependency chains exist in this repository
- The repository structure suggests this is example code rather than a complete infrastructure codebase
- Vagrant-based testing environment is suitable for continued development and testing