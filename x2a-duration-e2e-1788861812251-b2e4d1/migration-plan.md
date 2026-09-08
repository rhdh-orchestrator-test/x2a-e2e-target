# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains demonstration examples of Chef InSpec integration with Ansible playbooks rather than traditional Chef cookbooks requiring migration. The content is primarily educational/example code showing compliance automation patterns. The migration scope is minimal as the infrastructure automation is already implemented in Ansible, with Chef InSpec providing compliance verification.

## Module Migration Plan

This repository contains example Ansible playbooks with Chef InSpec compliance testing that demonstrate integration patterns rather than production infrastructure requiring migration:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup for a simple "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

**ssl-security-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2+ for POODLE vulnerability mitigation
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: SSL protocol configuration, Apache SSL module hardening, service restart handlers

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with Vagrant driver and InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests verifying HTTPS functionality, SSL protocol security, and web service availability
- `tests/ssh_profile.rb`: Chef InSpec security control testing SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test content for web server verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

**No external dependencies requiring migration** - The Ansible playbooks use standard modules:
- **apt module**: Native Ansible package management (no replacement needed)
- **openssl_* modules**: Native Ansible SSL/TLS certificate management (no replacement needed)
- **file/copy modules**: Native Ansible file operations (no replacement needed)
- **service module**: Native Ansible service management (no replacement needed)

### Security Considerations

**Compliance Testing Integration**: 
- Current Chef InSpec tests provide STIG compliance verification and SSL security validation
- Migration approach: Replace Chef InSpec with Ansible native testing using `ansible.builtin.assert` or integrate with `ansible-lint` security rules
- SSL/TLS certificate management uses self-signed certificates suitable for testing but requires proper CA certificates for production

**Credential Management**:
- No hardcoded credentials detected in the reviewed playbooks
- SSH key management handled through standard Ansible patterns
- SSL certificates generated dynamically without embedded secrets

### Technical Challenges

**Minimal Migration Complexity**: 
- Infrastructure automation already implemented in Ansible - no Chef cookbook conversion required
- Primary challenge is replacing Chef InSpec compliance testing framework with Ansible-native alternatives
- Test Kitchen integration may need replacement with molecule or native Ansible testing approaches

**InSpec Replacement Strategy**:
- Replace Chef InSpec compliance tests with Ansible `ansible.builtin.uri` module for HTTP/HTTPS verification
- Use Ansible `ansible.builtin.wait_for` module for port availability testing
- Implement SSL protocol verification using `ansible.builtin.openssl_certificate_info` module

### Migration Order

1. **Compliance Test Migration** (low risk, immediate value)
   - Convert InSpec tests to Ansible native verification tasks
   - Implement Ansible-based security compliance checking

2. **Test Framework Migration** (moderate complexity)
   - Replace Test Kitchen with Molecule for Ansible playbook testing
   - Migrate Vagrant-based testing to container or cloud-based testing

3. **Documentation and Training** (low complexity)
   - Update example documentation to reflect pure Ansible approach
   - Create training materials for Ansible-native compliance patterns

### Assumptions

- The repository serves as educational/demonstration content rather than production infrastructure requiring migration
- Current Ansible playbooks are functional and do not require significant refactoring beyond compliance testing integration
- Target environment will continue using Ubuntu/Debian-based systems as indicated by apt package manager usage
- Self-signed SSL certificates are acceptable for demonstration purposes, though production deployment would require proper certificate authority integration
- Test Kitchen and Chef InSpec dependencies are acceptable to maintain for demonstration purposes, or organization prefers migration to pure Ansible testing frameworks
- The setup scripts for Chef Automate/Server are for demonstration environment provisioning and not part of the core infrastructure automation requiring migration