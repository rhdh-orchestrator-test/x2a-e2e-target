# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains demonstration examples of using Chef InSpec for compliance testing alongside Ansible playbooks. The migration involves consolidating the existing Ansible playbooks and replacing Chef InSpec tests with native Ansible testing approaches. The scope is limited with low complexity due to the small number of playbooks and straightforward compliance requirements.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec compliance tests that need consolidation and native Ansible testing implementation:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, SSL virtual host configuration, directory structure creation

**poodle-ssl-fix**:
- Description: SSL security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2 only in Apache configuration
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: SSL protocol replacement in Apache configuration, service restart handlers for apache2 and sshd

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification in Vagrant/Ubuntu 20.04 environment
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality, SSL protocol security, and web content
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security control testing SSH root login restrictions (STIG compliance)
- `chef-and-ansible/index.html`: Static HTML test file for web server verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for lab environments
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

**No external dependencies requiring migration** - The Ansible playbooks are already functional and use standard Ansible modules:
- `apt` module for package management
- `openssl_*` modules for certificate generation
- `copy` and `file` modules for configuration management
- `command` module for Apache site management

### Security Considerations

**SSL/TLS Certificate Management**:
- Current implementation uses self-signed certificates generated via OpenSSL Ansible modules
- Migration approach: Maintain existing certificate generation or integrate with proper CA/Let's Encrypt
- Certificate files stored in `/etc/apache2/certs/` with appropriate permissions (0640)

**SSH Security Hardening**:
- InSpec test verifies PermitRootLogin is disabled
- Migration approach: Convert InSpec control to Ansible assert tasks or molecule tests
- STIG compliance requirement (RHEL-08-000227) needs native Ansible verification

**Apache Security Configuration**:
- SSL protocol hardening disables SSL3 and enforces TLS 1.2
- Migration approach: Expand security configuration to include additional Apache hardening measures
- Current regex-based configuration replacement should be enhanced with template-based approach

**Credential Management**:
- No hardcoded credentials detected in playbooks
- Chef Automate deployment scripts contain example credentials that should be externalized
- Migration approach: Use Ansible Vault for sensitive deployment variables

### Technical Challenges

**InSpec to Ansible Testing Migration**:
- Challenge: Converting Chef InSpec compliance tests to native Ansible testing framework
- Mitigation strategy: Implement Ansible assert tasks, molecule tests, or testinfra for compliance verification
- Specific conversions needed:
  - Port 443 listening verification → `wait_for` module with port check
  - HTTPS response testing → `uri` module with SSL verification disabled
  - SSL protocol testing → Custom fact gathering or external SSL testing tools

**Test Kitchen Integration Replacement**:
- Challenge: Replacing Test Kitchen workflow with Ansible-native testing
- Mitigation strategy: Implement Molecule for testing Ansible playbooks with multiple platforms
- Configuration migration from kitchen.yml to molecule.yml format

**Apache Configuration Management**:
- Challenge: Current regex-based SSL configuration replacement is brittle
- Mitigation strategy: Replace with Jinja2 templates for better maintainability and configuration management

### Migration Order

1. **website-https-deployment** (Priority 1: Core functionality, low risk)
   - Already in Ansible format, requires testing framework migration only
   - Convert InSpec tests to Ansible assert tasks
   - Implement proper Apache configuration templating

2. **poodle-ssl-fix** (Priority 2: Security hardening, moderate complexity)
   - Integrate SSL hardening into main website deployment playbook
   - Expand security configuration beyond just SSL protocol settings
   - Add comprehensive SSL/TLS security testing

3. **Testing Framework Migration** (Priority 3: Infrastructure, high complexity)
   - Replace Test Kitchen with Molecule
   - Convert all InSpec tests to Ansible-native testing approaches
   - Implement CI/CD pipeline for automated testing

### Assumptions

- **Target Environment**: Assuming continued use of Ubuntu/Debian-based systems due to apt package manager usage
- **Certificate Strategy**: Assuming self-signed certificates are acceptable for development/testing; production deployment may require proper CA integration
- **Testing Requirements**: Assuming compliance testing requirements remain the same but can be implemented with Ansible-native tools
- **Infrastructure Scope**: Assuming this is a demonstration/learning repository rather than production infrastructure
- **Apache Version**: Playbook specifies exact Apache version (2.4.41-4ubuntu3.10) which may need updating for newer Ubuntu releases
- **SSH Configuration**: Assuming SSH hardening requirements remain consistent with current InSpec controls
- **Deployment Scripts**: Chef Automate deployment scripts appear to be for lab setup and may not require migration if Chef infrastructure is being retired
- **Network Configuration**: Assuming localhost testing environment; production deployment may require additional network security considerations
- **SSL Protocol Requirements**: Assuming TLS 1.2 minimum requirement is still current; may need updating to TLS 1.3 for enhanced security