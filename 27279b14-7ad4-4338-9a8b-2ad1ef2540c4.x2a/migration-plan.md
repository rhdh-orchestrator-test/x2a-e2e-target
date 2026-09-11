# MIGRATION FROM CHEF TO ANSIBLE

This repository is a Chef examples repository that demonstrates Chef InSpec integration with Ansible playbooks. It contains NO traditional Chef cookbooks requiring migration to Ansible. The repository already contains functional Ansible playbooks and uses Chef InSpec only for compliance testing. The migration focus is on replacing Chef InSpec testing with Ansible-native alternatives.

**Migration Complexity**: Low
**Estimated Timeline**: 1-2 weeks  
**Primary Challenge**: Replacing Chef InSpec compliance testing framework

## Module Migration Plan

This repository contains demonstration and infrastructure content rather than traditional Chef cookbooks:

### MODULE INVENTORY

**NO CHEF COOKBOOKS FOUND**: This repository does not contain any Chef cookbooks with `recipes/default.rb` files, Puppet modules with `manifests/init.pp` files, or PowerShell modules with `.psd1` manifests that require migration to Ansible.

The repository contains:
- Ansible playbooks (already in target format)
- Chef InSpec compliance tests (Ruby-based testing framework)
- Infrastructure deployment scripts (Bash)

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for Apache HTTPS site deployment with SSL certificate management  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disables SSLv3, enables TLS 1.2)
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance profile for SSH security configuration
- `chef-and-ansible/index.html`: Static HTML test content
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml driver)  
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native compliance testing using molecule, testinfra, or ansible-lint
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and validation
- **Chef Automate/Infra Server**: Evaluate continued need for Chef infrastructure in pure Ansible environment

### Security Considerations

- **SSL Certificate Management**: Current playbooks use self-signed certificates - consider Let's Encrypt integration for production
- **Hardcoded Credentials**: Setup scripts contain hardcoded passwords (`userpassword='password'`) that should be moved to Ansible Vault
- **SSH Security Compliance**: InSpec profile validates SSH root login disabled - maintain equivalent Ansible-based validation
- **SSL Protocol Enforcement**: POODLE fix demonstrates security hardening - preserve these controls in migrated solution

### Technical Challenges

- **InSpec Test Conversion**: Converting Ruby-based InSpec tests to Ansible-native testing requires rewriting test assertions and validation logic
- **Test Kitchen Migration**: Moving from Test Kitchen to Molecule requires configuration restructuring and new testing workflows
- **Chef Infrastructure Dependencies**: Deployment scripts install Chef components that may be unnecessary in pure Ansible environment
- **Compliance Automation**: Establishing equivalent compliance validation without Chef InSpec toolchain

### Migration Order

1. **Evaluate Infrastructure Needs** (determine if Chef Automate deployment scripts are still required)
2. **Test Framework Migration** (replace InSpec tests with Molecule or testinfra)  
3. **Security Hardening Validation** (ensure SSL and SSH compliance checks remain functional)
4. **Documentation Updates** (update README and examples for pure Ansible workflow)

### Assumptions

- The existing Ansible playbooks represent the desired configuration management approach and require no changes
- Chef InSpec compliance testing should be replaced rather than maintained alongside Ansible
- Chef Automate/Infra Server infrastructure may no longer be needed in a pure Ansible environment
- Current SSL certificate approach (self-signed) is acceptable for demonstration purposes
- Ubuntu 20.04 and Vagrant testing environment specifications remain valid
- Hardcoded credentials in deployment scripts are acceptable for examples but would need Ansible Vault for production use
- The compliance requirements currently validated by InSpec tests remain relevant and need equivalent Ansible-based validation