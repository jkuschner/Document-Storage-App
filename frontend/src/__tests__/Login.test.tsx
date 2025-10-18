import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Login from "../components/Auth/Login.tsx";
import "@testing-library/jest-dom";

test("renders login form", () => {
  render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>
  );

  const emailInput = screen.queryByLabelText(/email/i) || screen.queryByPlaceholderText(/email/i) || document.querySelector('input[type="email"]');

  expect(emailInput).toBeInTheDocument();
});

test("handles input changes", () => {
  render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>
  );

  const emailInput = screen.queryByLabelText(/email/i) || screen.queryByPlaceholderText(/email/i) || document.querySelector('input[type="email"]');

  expect(emailInput).toBeInTheDocument();

  fireEvent.change(emailInput as HTMLInputElement, {
    target: { value: "test@example.com" },
  });

  expect((emailInput as HTMLInputElement).value).toBe("test@example.com");
});
