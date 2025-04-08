# Copyright (C) 2025 <xdc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import threading

def daemon(func, *args, **kwargs):
	thread = threading.Thread(target=func, args=args, kwargs=kwargs)
	thread.daemon = True  # 设置为守护线程
	thread.start()
	return thread
