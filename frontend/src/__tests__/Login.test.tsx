
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
  /*expect(screen.getByText(/Login/i)).toBeInTheDocument();*/
  const loginHeading = screen.getByRole("heading", { name: /login/i });
  expect(loginHeading).toBeInTheDocument();

});

test("handles input changes", () => {
  render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>
  );
  /*const emailInput = screen.getByLabelText(/email/i);
  fireEvent.change(emailInput, { target: { value: "test@example.com" } });
  expect((emailInput as HTMLInputElement).value).toBe("test@example.com");
  */

  /*const emailInput = screen.getByRole("textbox", { name: /email/i }) as HTMLInputElement;
  fireEvent.change(emailInput, { target: { value: "test@example.com" } });
  expect(emailInput.value).toBe("test@example.com");*/

  const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
  fireEvent.change(emailInput, { target: { value: "test@example.com" } });
  expect(emailInput.value).toBe("test@example.com");

});
