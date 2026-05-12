import nextConfig from "eslint-config-next";

const eslintConfig = [
  ...nextConfig,
  {
    rules: {
      // Downgrade strict React 19 hooks rules to warnings so CI doesn't
      // block on pre-existing patterns while the team cleans them up.
      "react-hooks/set-state-in-effect": "warn",
      "react-hooks/immutability": "warn",
      "react-hooks/use-memo": "warn",
      "import/no-anonymous-default-export": "warn",
    },
  },
];

export default eslintConfig;
