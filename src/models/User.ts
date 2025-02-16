import { UUID } from "crypto";

type User = {
	id: UUID
	email: string,
	password: string,
}

export default User;
