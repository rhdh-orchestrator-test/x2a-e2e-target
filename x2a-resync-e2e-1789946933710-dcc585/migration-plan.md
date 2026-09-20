# MIGRATION FROM CHEF INFRASTRUCTURE TO ANSIBLE

This repository contains Chef infrastructure deployment scripts and Ansible playbook examples demonstrating compliance automation. The migration scope is limited as the primary configuration management is already implemented in Ansible playbooks. The main migration effort involves replacing Chef Automate/InSpec infrastructure with native Ansible testing and compliance solutions.

**Timeline Estimate**: 2-4 weeks
**Complexity**: Low to Medium
**Risk Level**: Low (existing Ansible playbooks reduce migration complexity)

## Module Migration Plan

This repository contains Chef infrastructure deployment scripts and Ansible demonstration playbooks that need migration planning:

### MODULE INVENTORY

**chef-infrastructure-deployment**:
- Description: Chef Automate and Chef Infra Server deployment automation with user and organization provisioning
- Path: setup-automate/
- Technology: Bash scripts for Chef infrastructure
- Key Features: Automated Chef Automate deployment, Chef Infra Server setup, user/org creation, system tuning

**website-https-demo**:
- Description: Apache web server with SSL/TLS configuration and self-signed certificate generation
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4 installation, SSL certificate generation, virtual host configuration, security hardening

**ssl-security-fix**:
- Description: Apache SSL protocol hardening to disable vulnerable SSL protocols
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: SSL protocol restriction, TLS 1.2 enforcement, POODLE vulnerability mitigation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL configuration
- `tests/ssh_profile.rb`: InSpec security compliance tests for SSH root login restrictions
- `index.html`: Static web content for testing purposes
- `README.md`: Documentation explaining Chef InSpec integration with Ansible

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate**: Replace with Ansible AWX/Tower for automation platform and compliance reporting
- **Chef InSpec**: Migrate to ansible-lint, molecule testing, or integrate with external compliance tools like OpenSCAP
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and verification
- **Chef Infra Server**: Eliminate dependency as configuration management is handled by Ansible

### Security Considerations

- **SSL/TLS Configuration**: Existing Ansible playbooks already implement proper SSL hardening practices
  - Self-signed certificate generation using OpenSSL modules
  - SSL protocol restrictions (TLS 1.2 enforcement)
  - Proper file permissions for certificate files (0640)
- **SSH Security**: InSpec tests verify SSH root login restrictions - migrate to Ansible security role
- **Credential Management**: 
  - Hardcoded credentials in Chef deployment scripts (userpassword='password')
  - Chef user and organization PEM files need secure handling
  - No vault usage detected in current implementation

### Technical Challenges

- **Compliance Testing Migration**: InSpec tests need conversion to Ansible-native testing frameworks
  - Port listening verification (port 443)
  - HTTP response validation
  - SSL protocol compliance checks
  - SSH configuration validation
- **Infrastructure Deployment**: Chef Automate deployment scripts need replacement with Ansible-based infrastructure provisioning
- **Test Integration**: Kitchen.yml workflow needs migration to Molecule or CI/CD pipeline integration

### Migration Order

1. **Infrastructure Provisioning** (setup-automate/ scripts) - Replace Chef infrastructure deployment with Ansible-based provisioning
2. **Compliance Testing Framework** (InSpec tests) - Migrate to Ansible testing tools (molecule, ansible-lint, or external compliance integration)
3. **CI/CD Integration** (kitchen.yml) - Replace Test Kitchen workflow with Molecule or native CI/CD testing

### Assumptions

- The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are production-ready and do not require migration
- Chef Automate is currently used for compliance reporting and automation orchestration
- The target environment supports Ansible AWX/Tower as a replacement for Chef Automate
- InSpec compliance tests represent actual organizational security requirements that must be preserved
- The deployment scripts are used in production environments and not just for demonstration purposes
- Network connectivity and firewall rules allow Ansible management traffic on standard ports (22, 5986)
- The Ubuntu 20.04 target platform will be maintained or upgraded to a supported version during migration