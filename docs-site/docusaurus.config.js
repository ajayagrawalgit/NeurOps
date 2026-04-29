// @ts-check

module.exports = {
  title: 'NeurOps',
  tagline: 'Next Generation Neural Operations',
  url: 'https://neurops.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'NeuronOps', // Usually your GitHub org/user name.
  projectName: 'NeurOps', // Usually your repo name.
  themes: ['@docusaurus/theme-classic'],
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarsPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl: 'https://github.com/NeuronOps/NeurOps/edit/main/','.Docusaurus/docs/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};