import * as jwt from 'jsonwebtoken';

class RefreshTokenController {
	public static getToken (req): string {
		if (req.headers.authorization && req.headers.authorization.split(' ')[0] === 'Bearer') {
			return req.headers.authorization.split(' ')[1];
		} else if (req.query && req.query.token) {
			return req.query.token;
		}

		return '';
	}
}

export default RefreshTokenController;
