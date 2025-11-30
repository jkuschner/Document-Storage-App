/*
import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
*/
import React from 'react';
import { render, waitFor, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import App from './App';

test("renders login page", async () => {
  render(<App />);

  // Wait for the login page to actually appear after loading finishes
  const loginHeading = await waitFor(() =>
    screen.getByRole("heading", { name: /login/i })
  );

  expect(loginHeading).toBeInTheDocument();
});

