# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and demonstration materials that showcase integration between Chef InSpec and Ansible for compliance automation. The migration scope is limited as this is primarily a demonstration/example repository rather than production infrastructure code. The main migration effort involves consolidating the existing Ansible playbooks and Chef InSpec tests into a cohesive Ansible-based compliance automation framework.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low (demonstration code, no production dependencies)

## Module Migration Plan

This repository contains demonstration materials and example configurations that showcase Chef InSpec integration with Ansible:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file search tools.

**chef-and-ansible**:
- Description: Ansible playbooks demonstrating Apache HTTPS configuration with SSL/TLS security hardening and Chef InSpec compliance testing
- Path: chef-and-ansible/
- Technology: Ansible (already migrated) + Chef InSpec
- Key Features: Apache 2.4.41 installation, self-signed SSL certificate generation, virtual host configuration, POODLE vulnerability mitigation, InSpec compliance verification

**setup-automate**:
- Description: Bash deployment scripts for Chef Automate and Chef Infra Server installation and initial configuration
- Path: setup-automate/
- Technology: Bash scripts + Chef server management
- Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `website_https.yml`: Ansible playbook for Apache HTTPS setup with SSL certificate management
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disabling SSLv3, enabling TLSv1.2)
- `website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol verification
- `ssh_profile.rb`: Chef InSpec compliance profile for SSH security configuration (STIG compliance)
- `deploy-automate.sh`: Chef Automate deployment automation script
- `deploy-chef-server.sh`: Chef Infra Server deployment automation script
- `index.html`: Static web content for testing purposes

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible compliance modules or maintain InSpec integration via ansible.posix.inspec
- **Test Kitchen**: Replace with molecule for Ansible playbook testing
- **Chef Automate/Server**: Evaluate need for centralized compliance reporting - consider Ansible Tower/AWX or external SIEM integration
- **Vagrant**: Continue using for local development or migrate to container-based testing

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks already implement proper SSL certificate generation and Apache SSL hardening
  - Self-signed certificate generation using openssl_* modules
  - SSL protocol restrictions (TLSv1.2 only, SSLv3 disabled)
  - Proper file permissions on certificate files (0640)
- **SSH Hardening**: InSpec profile enforces SSH root login restrictions
  - Migration approach: Convert InSpec controls to Ansible tasks using lineinfile or template modules
- **Vault/secrets management**: 
  - Current implementation uses plaintext variables in playbooks
  - 2 credential patterns detected: SSH configuration and SSL certificate management
  - Recommendation: Implement Ansible Vault for sensitive data encryption

### Technical Challenges

- **InSpec Integration**: Decision needed on whether to maintain Chef InSpec or migrate to native Ansible compliance
  - Challenge: InSpec provides rich compliance reporting and STIG profile compatibility
  - Mitigation: Evaluate ansible.posix.inspec module or migrate to ansible.builtin.assert with custom compliance tasks
- **Test Framework Migration**: Kitchen.yml uses Test Kitchen with Ansible provisioner
  - Challenge: Test Kitchen is Chef ecosystem tooling
  - Mitigation: Migrate to Molecule for native Ansible testing with pytest or testinfra
- **Compliance Reporting**: Chef InSpec provides structured compliance reporting
  - Challenge: Ansible lacks equivalent built-in compliance reporting
  - Mitigation: Implement custom reporting using ansible.builtin.uri to external systems or maintain InSpec integration

### Migration Order

1. **setup-automate** (Priority 1: Infrastructure deployment scripts)
   - Convert bash scripts to Ansible playbooks for Chef server deployment
   - Low complexity, high value for automation consistency
2. **chef-and-ansible compliance integration** (Priority 2: Core functionality)
   - Evaluate InSpec integration strategy
   - Migrate or maintain existing compliance tests
3. **Testing framework** (Priority 3: Development workflow)
   - Migrate from Test Kitchen to Molecule
   - Update CI/CD pipelines if applicable

### Assumptions

- This is a demonstration/example repository, not production infrastructure requiring migration
- The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already properly structured and functional
- Chef InSpec integration may be intentionally maintained for demonstration purposes rather than migrated away
- No production dependencies or downstream systems rely on these examples
- The repository serves as educational/reference material for Chef-Ansible integration patterns
- Ubuntu 20.04 target platform assumption based on kitchen.yml configuration may need validation for actual deployment targets
- Vagrant-based testing environment assumption may not reflect production deployment requirements
- No external Chef server dependencies exist beyond the local deployment scripts
- SSL certificate management is acceptable with self-signed certificates for demonstration purposes
- No integration with external PKI or certificate authorities is required
- The hardcoded credentials in deployment scripts are acceptable for demonstration but would need Ansible Vault in production use